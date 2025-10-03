import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import engine
from app.database.base import Base
from app.models.user import User
from app.models.news import News
from app.models.comment import Comment

print("Creating database tables in PostgreSQL...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")

# Verify tables were created
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';"))
    tables = [row[0] for row in result]
    print(f"✅ Tables created: {tables}")
    
    # Count records in each table
    for table in tables:
        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
        count = count_result.scalar()
        print(f"   {table}: {count} records")
