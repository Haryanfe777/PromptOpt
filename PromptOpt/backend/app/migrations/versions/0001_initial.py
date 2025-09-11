from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
	op.create_table('users',
		sa.Column('id', sa.Integer(), primary_key=True),
		sa.Column('username', sa.String(length=100), nullable=False, index=True, unique=True),
		sa.Column('password_hash', sa.String(length=255), nullable=False),
		sa.Column('role', sa.String(length=20), nullable=False, index=True),
		sa.Column('created_at', sa.DateTime(), nullable=True),
	)

	op.create_table('prompts',
		sa.Column('id', sa.Integer(), primary_key=True),
		sa.Column('title', sa.String(length=200), nullable=False),
		sa.Column('created_by', sa.String(length=100), nullable=False),
		sa.Column('created_at', sa.DateTime(), nullable=True),
	)

	op.create_table('prompt_versions',
		sa.Column('id', sa.Integer(), primary_key=True),
		sa.Column('prompt_id', sa.Integer(), sa.ForeignKey('prompts.id'), nullable=False),
		sa.Column('version', sa.Integer(), nullable=False),
		sa.Column('content', sa.Text(), nullable=False),
		sa.Column('is_active', sa.Boolean(), default=True),
		sa.Column('created_at', sa.DateTime(), nullable=True),
	)

	op.create_table('conversations',
		sa.Column('id', sa.Integer(), primary_key=True),
		sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
		sa.Column('prompt_version_id', sa.Integer(), sa.ForeignKey('prompt_versions.id'), nullable=True),
		sa.Column('started_at', sa.DateTime(), nullable=True),
	)

	op.create_table('messages',
		sa.Column('id', sa.Integer(), primary_key=True),
		sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id'), nullable=False),
		sa.Column('role', sa.String(length=20), nullable=False),
		sa.Column('content', sa.Text(), nullable=False),
		sa.Column('created_at', sa.DateTime(), nullable=True),
	)

	op.create_table('evaluations',
		sa.Column('id', sa.Integer(), primary_key=True),
		sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id'), nullable=False),
		sa.Column('message_id', sa.Integer(), sa.ForeignKey('messages.id'), nullable=True),
		sa.Column('overall', sa.Float(), nullable=False),
		sa.Column('criteria', sa.JSON(), nullable=False),
		sa.Column('label', sa.String(length=50), nullable=True),
		sa.Column('judge_model', sa.String(length=100), nullable=True),
		sa.Column('created_at', sa.DateTime(), nullable=True),
	)

	op.create_table('guardrails',
		sa.Column('id', sa.Integer(), primary_key=True),
		sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id'), nullable=False),
		sa.Column('message_id', sa.Integer(), sa.ForeignKey('messages.id'), nullable=True),
		sa.Column('action', sa.String(length=20), nullable=False),
		sa.Column('report', sa.JSON(), nullable=False),
		sa.Column('created_at', sa.DateTime(), nullable=True),
	)


def downgrade():
	op.drop_table('guardrails')
	op.drop_table('evaluations')
	op.drop_table('messages')
	op.drop_table('conversations')
	op.drop_table('prompt_versions')
	op.drop_table('prompts')
	op.drop_table('users')
