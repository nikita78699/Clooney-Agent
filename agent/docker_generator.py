from typing import Dict
import os
import yaml

class DockerGenerator:
    def __init__(self):
        self.output_dir = "output/backend"
        
    def generate_dockerfile(self):
        """Generate Dockerfile for FastAPI backend"""
        dockerfile = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        with open(f"{self.output_dir}/Dockerfile", "w") as f:
            f.write(dockerfile)
    
    def generate_docker_compose(self):
        """Generate docker-compose.yml"""
        compose = '''version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: asana_clone
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/asana_clone
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./app:/app/app

volumes:
  postgres_data:
'''
        with open(f"{self.output_dir}/docker-compose.yml", "w") as f:
            f.write(compose)
    
    def generate_alembic_config(self):
        """Generate Alembic configuration"""
        os.makedirs(f"{self.output_dir}/alembic", exist_ok=True)
        
        alembic_ini = '''[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''
        with open(f"{self.output_dir}/alembic.ini", "w") as f:
            f.write(alembic_ini)
        
        # Alembic env.py
        env_py = '''from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.models import *

config = context.config
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/asana_clone'))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        with open(f"{self.output_dir}/alembic/env.py", "w") as f:
            f.write(env_py)
        
        # Alembic script.py.mako
        script_mako = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''
        with open(f"{self.output_dir}/alembic/script.py.mako", "w") as f:
            f.write(script_mako)
        
        os.makedirs(f"{self.output_dir}/alembic/versions", exist_ok=True)
    
    def generate_schema_sql(self, db_schema: Dict):
        """Generate schema.sql file"""
        sql_statements = []
        
        for table_name, schema in db_schema.items():
            columns = []
            for col in schema["columns"]:
                col_def = f'  {col["name"]} {col["type"]}'
                if not col.get("nullable", True):
                    col_def += " NOT NULL"
                if col.get("default"):
                    col_def += f' DEFAULT {col["default"]}'
                columns.append(col_def)
            
            # Add foreign key constraints
            for rel in schema.get("relationships", []):
                fk_constraint = f'  FOREIGN KEY ({rel["field"]}) REFERENCES {rel["references"]}(id) ON DELETE CASCADE'
                columns.append(fk_constraint)
            
            create_table = f'CREATE TABLE {table_name} (\n' + ',\n'.join(columns) + '\n);\n'
            sql_statements.append(create_table)
        
        schema_sql = '\n'.join(sql_statements)
        with open(f"{self.output_dir}/schema.sql", "w") as f:
            f.write(schema_sql)
