"""Add mock data

Revision ID: 002
Revises: 001
Create Date: 2023-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Create table objects for data insertion
    users_table = table('users',
        column('name', sa.String),
        column('email', sa.String),
        column('is_verified', sa.Boolean),
        column('avatar', sa.Text),
        column('created_at', sa.DateTime)
    )
    
    news_table = table('news',
        column('title', sa.String),
        column('content', sa.JSON),
        column('cover', sa.Text),
        column('author_id', sa.Integer),
        column('created_at', sa.DateTime)
    )
    
    comments_table = table('comments',
        column('text', sa.Text),
        column('news_id', sa.Integer),
        column('author_id', sa.Integer),
        column('created_at', sa.DateTime)
    )

    # Insert mock users
    op.bulk_insert(users_table, [
        {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'is_verified': True,
            'avatar': 'https://example.com/avatar1.jpg',
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'is_verified': True,
            'avatar': 'https://example.com/avatar2.jpg',
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Bob Johnson',
            'email': 'bob.johnson@example.com',
            'is_verified': False,
            'avatar': 'https://example.com/avatar3.jpg',
            'created_at': datetime.utcnow()
        }
    ])

    # Insert mock news
    op.bulk_insert(news_table, [
        {
            'title': 'First News Article',
            'content': {'blocks': [{'type': 'paragraph', 'text': 'This is the first news article content.'}]},
            'cover': 'https://example.com/cover1.jpg',
            'author_id': 1,
            'created_at': datetime.utcnow()
        },
        {
            'title': 'Second News Article',
            'content': {'blocks': [{'type': 'paragraph', 'text': 'This is the second news article content.'}]},
            'cover': 'https://example.com/cover2.jpg',
            'author_id': 2,
            'created_at': datetime.utcnow()
        }
    ])

    # Insert mock comments
    op.bulk_insert(comments_table, [
        {
            'text': 'Great article!',
            'news_id': 1,
            'author_id': 2,
            'created_at': datetime.utcnow()
        },
        {
            'text': 'Very informative, thanks!',
            'news_id': 1,
            'author_id': 3,
            'created_at': datetime.utcnow()
        },
        {
            'text': 'Looking forward to more content like this.',
            'news_id': 2,
            'author_id': 1,
            'created_at': datetime.utcnow()
        }
    ])

def downgrade():
    op.execute("DELETE FROM comments")
    op.execute("DELETE FROM news")
    op.execute("DELETE FROM users")
