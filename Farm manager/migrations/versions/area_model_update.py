"""Atualização do modelo de área para geolocalização

Revision ID: area_model_update
Revises: 
Create Date: 2023-06-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'area_model_update'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Renomear colunas existentes para os nomes em português
    op.alter_column('area', 'name', new_column_name='nome', existing_type=sa.String(100))
    op.alter_column('area', 'size', new_column_name='tamanho', existing_type=sa.Float)
    op.alter_column('area', 'location', new_column_name='endereco', existing_type=sa.String(200))
    
    # Adicionar novas colunas
    op.add_column('area', sa.Column('cultura', sa.String(50), server_default='soja'))
    op.add_column('area', sa.Column('latitude', sa.String(30), nullable=True))
    op.add_column('area', sa.Column('longitude', sa.String(30), nullable=True))
    op.add_column('area', sa.Column('descricao', sa.Text(), nullable=True))


def downgrade():
    # Remover novas colunas
    op.drop_column('area', 'descricao')
    op.drop_column('area', 'longitude')
    op.drop_column('area', 'latitude')
    op.drop_column('area', 'cultura')
    
    # Reverter nomes de colunas para o inglês
    op.alter_column('area', 'nome', new_column_name='name', existing_type=sa.String(100))
    op.alter_column('area', 'tamanho', new_column_name='size', existing_type=sa.Float)
    op.alter_column('area', 'endereco', new_column_name='location', existing_type=sa.String(200)) 