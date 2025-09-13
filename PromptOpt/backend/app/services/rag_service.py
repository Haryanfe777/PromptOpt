import os
import json
from typing import List, Tuple, Dict
import numpy as np
import faiss
from pypdf import PdfReader
import openai

INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
INDEX_PATH = os.path.join(INDEX_DIR, "company.faiss")
META_PATH = os.path.join(INDEX_DIR, "company_meta.jsonl")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

class RAGService:
	def __init__(self):
		self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))
		os.makedirs(INDEX_DIR, exist_ok=True)
		self.index = None
		self.meta: List[dict] = []
		self._load()

	def _load(self):
		if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
			self.index = faiss.read_index(INDEX_PATH)
			with open(META_PATH, "r", encoding="utf-8") as f:
				self.meta = [json.loads(l) for l in f]

	def _save(self):
		if self.index is not None:
			faiss.write_index(self.index, INDEX_PATH)
		with open(META_PATH, "w", encoding="utf-8") as f:
			for m in self.meta:
				f.write(json.dumps(m, ensure_ascii=False) + "\n")

	def _ensure_loaded(self):
		if (self.index is None or not self.meta) and os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
			self._load()

	def _embed(self, texts: List[str]) -> np.ndarray:
		res = self.client.embeddings.create(model=EMBED_MODEL, input=texts)
		vecs = [np.array(e.embedding, dtype=np.float32) for e in res.data]
		return np.vstack(vecs)

	def ingest_pdf(self, pdf_path: str, chunk_chars: int = 1200, overlap: int = 150) -> int:
		reader = PdfReader(pdf_path)
		text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
		chunks = []
		start = 0
		while start < len(text):
			end = min(len(text), start + chunk_chars)
			chunks.append(text[start:end])
			start = end - overlap
			if start < 0:
				start = 0
			if end == len(text):
				break
		if not chunks:
			return 0
		vecs = self._embed(chunks)
		if self.index is None:
			self.index = faiss.IndexFlatIP(vecs.shape[1])
		faiss.normalize_L2(vecs)
		self.index.add(vecs)
		for i, chunk in enumerate(chunks):
			self.meta.append({"text": chunk[:1000], "source": os.path.basename(pdf_path), "idx": len(self.meta)})
		self._save()
		return len(chunks)

	def status(self) -> dict:
		self._ensure_loaded()
		return {"documents": len(self.meta), "has_index": self.index is not None}

	def retrieve(self, query: str, top_k: int = 4) -> List[Tuple[str, float, dict]]:
		self._ensure_loaded()
		if self.index is None or not self.meta:
			return []
		q = self._embed([query])
		faiss.normalize_L2(q)
		dists, idxs = self.index.search(q, top_k)
		out = []
		for rank, (i, d) in enumerate(zip(idxs[0], dists[0])):
			if i < 0 or i >= len(self.meta):
				continue
			m = self.meta[i]
			out.append((m["text"], float(d), m))
		return out

	def build_system_prompt_with_provenance(self, base_prompt: str, query: str, top_k: int = 4) -> Tuple[str, List[Dict]]:
		contexts = self.retrieve(query, top_k=top_k)
		if not contexts:
			return base_prompt, []
		ctx_block = "\n\n".join([f"[Source {i+1}]\n" + t for i, (t, _, _) in enumerate(contexts)])
		prov = [{"text": t, "score": s, "source": m.get("source")} for (t, s, m) in contexts]
		prompt = (
			f"{base_prompt}\n\n"
			f"Use ONLY the following company context to answer. If the answer is not in the context, say you cannot find it.\n"
			f"Context:\n{ctx_block}"
		)
		return prompt, prov
