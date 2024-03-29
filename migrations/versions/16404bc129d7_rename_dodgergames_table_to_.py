"""Rename DodgerGames Table to BaseballGames

Revision ID: 16404bc129d7
Revises: 1da3fb0633cb
Create Date: 2023-11-06 22:07:25.034633

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '16404bc129d7'
down_revision = '1da3fb0633cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.rename_table('dodger_games', 'baseball_games')

    #? When renaming a table, foreign keys that reference it MUST also be updated!
    #* Promos had a foreign key that linked to the dodger_game.id, so rename it to match the table's new name
    op.alter_column('promos', 'dodger_game_id', new_column_name='baseball_game_id', existing_type=sa.Integer)
    #? Use existing_type to ensure I can drop the ForeignKeyConstraint of this ForeignKeyColumn, an SQLAlchemy Schema type

    with op.batch_alter_table('promos', schema=None) as batch_op:
        #* Now that the dodger_game_id foreignKey column was renamed, drop its related constraint
        batch_op.drop_constraint('promos_dodger_game_id_fkey', type_='foreignkey')
        #? AND use the following to create a new foreign_key constraint linked to the renamed column using the renamed table
        batch_op.create_foreign_key('promos_baseball_game_id_fkey', 'baseball_games', ['baseball_game_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.rename_table('baseball_games', 'dodger_games')

    op.alter_column('promos', 'baseball_game_id', new_column_name='dodger_game_id', existing_type=sa.Integer)

    with op.batch_alter_table('promos', schema=None) as batch_op:
        batch_op.drop_constraint('promos_baseball_game_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key('promos_dodger_game_id_fkey', 'dodger_games', ['dodger_game_id'], ['id'])

    # ### end Alembic commands ###
