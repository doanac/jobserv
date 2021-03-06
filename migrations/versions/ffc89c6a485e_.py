# Copyright (C) 2017 Linaro Limited
# Author: Andy Doan <andy.doan@linaro.org>

"""empty message

Revision ID: ffc89c6a485e
Revises:
Create Date: 2017-08-15 11:47:11.251467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffc89c6a485e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('projects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('workers',
    sa.Column('name', sa.String(length=512), nullable=False),
    sa.Column('distro', sa.String(length=1024), nullable=False),
    sa.Column('mem_total', sa.BigInteger(), nullable=False),
    sa.Column('cpu_total', sa.Integer(), nullable=False),
    sa.Column('cpu_type', sa.String(length=1024), nullable=False),
    sa.Column('enlisted', sa.Boolean(), nullable=False),
    sa.Column('api_key', sa.String(length=1024), nullable=False),
    sa.Column('concurrent_runs', sa.Integer(), nullable=False),
    sa.Column('host_tags', sa.String(length=1024), nullable=True),
    sa.Column('online', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('builds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('build_id', sa.Integer(), nullable=False),
    sa.Column('proj_id', sa.Integer(), nullable=False),
    sa.Column('_status', sa.Integer(), nullable=True),
    sa.Column('reason', sa.String(length=4096), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('annotation', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['proj_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('proj_id', 'build_id', name='build_id_uc')
    )
    op.create_table('project_trigger',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user', sa.String(length=128), nullable=False),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('proj_id', sa.Integer(), nullable=False),
    sa.Column('definition_repo', sa.String(length=512), nullable=True),
    sa.Column('definition_file', sa.String(length=512), nullable=True),
    sa.Column('secrets', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['proj_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('build_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('_status', sa.Integer(), nullable=True),
    sa.Column('build_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['build_id'], ['builds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('runs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('build_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('_status', sa.Integer(), nullable=True),
    sa.Column('api_key', sa.String(length=80), nullable=False),
    sa.Column('trigger', sa.String(length=80), nullable=True),
    sa.Column('meta', sa.String(length=1024), nullable=True),
    sa.Column('worker_name', sa.String(length=512), nullable=True),
    sa.Column('host_tag', sa.String(length=1024), nullable=True),
    sa.ForeignKeyConstraint(['build_id'], ['builds.id'], ),
    sa.ForeignKeyConstraint(['worker_name'], ['workers.name'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('build_id', 'name', name='run_name_uc')
    )
    op.create_table('run_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('_status', sa.Integer(), nullable=True),
    sa.Column('run_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['run_id'], ['runs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('run_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=512), nullable=False),
    sa.Column('context', sa.String(length=1024), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('_status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['run_id'], ['runs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('test_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=1024), nullable=False),
    sa.Column('context', sa.String(length=1024), nullable=True),
    sa.Column('_status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_results')
    op.drop_table('tests')
    op.drop_table('run_events')
    op.drop_table('runs')
    op.drop_table('build_events')
    op.drop_table('project_trigger')
    op.drop_table('builds')
    op.drop_table('workers')
    op.drop_table('projects')
    # ### end Alembic commands ###
