#!/usr/bin/env python
from app.db import Base, Property, PriceHistory
from app.config import MYSQL_CONFIG
from sqlalchemy import create_engine
import os

# Update alembic.ini with MySQL connection string
def update_alembic_ini():
    connection_string = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}?charset={MYSQL_CONFIG['charset']}"
    
    with open('alembic.ini', 'r') as f:
        content = f.read()
    
    # Replace the default connection string
    content = content.replace(
        'sqlalchemy.url = driver://user:pass@localhost/dbname',
        f'sqlalchemy.url = {connection_string}'
    )
    
    with open('alembic.ini', 'w') as f:
        f.write(content)
    
    print("Updated alembic.ini with MySQL connection string")

# Update env.py to use our models metadata
def update_env_py():
    with open('migrations/env.py', 'r') as f:
        content = f.read()
    
    # Replace the target_metadata = None line
    content = content.replace(
        'target_metadata = None',
        'from app.db import Base\ntarget_metadata = Base.metadata'
    )
    
    with open('migrations/env.py', 'w') as f:
        f.write(content)
    
    print("Updated migrations/env.py to use our models metadata")

if __name__ == "__main__":
    update_alembic_ini()
    update_env_py()
    print("Migration script setup complete. Now run 'alembic revision --autogenerate -m \"initial\"' to create the initial migration")
