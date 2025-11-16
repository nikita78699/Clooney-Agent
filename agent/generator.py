from jinja2 import Template
import os
from typing import Dict

class CodeGenerator:
    def __init__(self, db_schema: Dict, api_spec: Dict):
        self.db_schema = db_schema
        self.api_spec = api_spec
        self.output_dir = "output/backend"
        
    def generate_all(self):
        """Generate all FastAPI code"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.generate_models()
        self.generate_database()
        self.generate_schemas()
        self.generate_crud()
        self.generate_routes()
        self.generate_main()
        self.generate_requirements()
        
    def generate_models(self):
        """Generate SQLAlchemy models"""
        code = '''from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    archived = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=True)
    due_on = Column(Date, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    gid = Column(String(255), unique=True, nullable=False, index=True)
    text = Column(Text, nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
'''
        
        os.makedirs(f"{self.output_dir}/app", exist_ok=True)
        with open(f"{self.output_dir}/app/models.py", "w") as f:
            f.write(code)
    
    def generate_database(self):
        """Generate database configuration"""
        code = '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/asana_clone")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        with open(f"{self.output_dir}/app/database.py", "w") as f:
            f.write(code)
    
    def generate_schemas(self):
        """Generate Pydantic schemas"""
        template = Template('''from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

{% for model_name, fields in api_schemas.items() %}
class {{ model_name }}Base(BaseModel):
{% for field, ftype in fields.items() %}
{% if field not in ['gid'] %}
{% if field in ['workspace', 'project', 'assignee', 'parent', 'task', 'created_by'] %}
    {{ field }}: Optional[str] = None
{% elif ftype == 'boolean' %}
    {{ field }}: Optional[bool] = None
{% elif ftype == 'date' %}
    {{ field }}: Optional[date] = None
{% else %}
    {{ field }}: Optional[str] = None
{% endif %}
{% endif %}
{% endfor %}

class {{ model_name }}Create({{ model_name }}Base):
    pass

class {{ model_name }}Update({{ model_name }}Base):
    pass

class {{ model_name }}({{ model_name }}Base):
    gid: str
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

{% endfor %}
''')
        
        code = template.render(api_schemas=self.api_spec.get("schemas", {}))
        with open(f"{self.output_dir}/app/schemas.py", "w") as f:
            f.write(code)
    
    def generate_crud(self):
        """Generate CRUD operations"""
        code = '''from sqlalchemy.orm import Session
from app import models, schemas
from typing import List, Optional
import uuid

# Tasks
def get_task(db: Session, task_gid: str):
    return db.query(models.Task).filter(models.Task.gid == task_gid).first()

def get_tasks_by_project(db: Session, project_gid: str):
    project = db.query(models.Project).filter(models.Project.gid == project_gid).first()
    if not project:
        return []
    return db.query(models.Task).filter(models.Task.project_id == project.id).all()

def get_tasks_by_section(db: Session, section_gid: str):
    section = db.query(models.Section).filter(models.Section.gid == section_gid).first()
    if not section:
        return []
    return db.query(models.Task).filter(models.Task.parent_id == section.id).all()

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(
        gid=str(uuid.uuid4()),
        **task.model_dump(exclude_unset=True)
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_gid: str, task: schemas.TaskUpdate):
    db_task = get_task(db, task_gid)
    if db_task:
        for key, value in task.model_dump(exclude_unset=True).items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_gid: str):
    db_task = get_task(db, task_gid)
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task

# Projects
def get_project(db: Session, project_gid: str):
    return db.query(models.Project).filter(models.Project.gid == project_gid).first()

def get_projects(db: Session, workspace_gid: str):
    workspace = db.query(models.Workspace).filter(models.Workspace.gid == workspace_gid).first()
    if not workspace:
        return []
    return db.query(models.Project).filter(models.Project.workspace_id == workspace.id).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        gid=str(uuid.uuid4()),
        **project.model_dump(exclude_unset=True)
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_gid: str, project: schemas.ProjectUpdate):
    db_project = get_project(db, project_gid)
    if db_project:
        for key, value in project.model_dump(exclude_unset=True).items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_gid: str):
    db_project = get_project(db, project_gid)
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project

# Sections
def get_sections(db: Session, project_gid: str):
    project = db.query(models.Project).filter(models.Project.gid == project_gid).first()
    if not project:
        return []
    return db.query(models.Section).filter(models.Section.project_id == project.id).all()

def create_section(db: Session, section: schemas.SectionCreate):
    section_data = section.model_dump(exclude_unset=True)
    
    # Convert project gid to project_id
    if 'project' in section_data:
        project_gid = section_data.pop('project')
        project = db.query(models.Project).filter(models.Project.gid == project_gid).first()
        if project:
            section_data['project_id'] = project.id
    
    db_section = models.Section(
        gid=str(uuid.uuid4()),
        **section_data
    )
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

def update_section(db: Session, section_gid: str, section: schemas.SectionUpdate):
    db_section = db.query(models.Section).filter(models.Section.gid == section_gid).first()
    if db_section:
        for key, value in section.model_dump(exclude_unset=True).items():
            setattr(db_section, key, value)
        db.commit()
        db.refresh(db_section)
    return db_section

def delete_section(db: Session, section_gid: str):
    db_section = db.query(models.Section).filter(models.Section.gid == section_gid).first()
    if db_section:
        db.delete(db_section)
        db.commit()
    return db_section

# Users
def get_user(db: Session, user_gid: str):
    return db.query(models.User).filter(models.User.gid == user_gid).first()

def get_users(db: Session, workspace_gid: str):
    workspace = db.query(models.Workspace).filter(models.Workspace.gid == workspace_gid).first()
    if not workspace:
        return []
    return db.query(models.User).filter(models.User.workspace_id == workspace.id).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        gid=str(uuid.uuid4()),
        **user.model_dump(exclude_unset=True)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Workspaces
def get_workspace(db: Session, workspace_gid: str):
    return db.query(models.Workspace).filter(models.Workspace.gid == workspace_gid).first()

def get_workspaces(db: Session):
    return db.query(models.Workspace).all()

def create_workspace(db: Session, workspace: schemas.WorkspaceCreate):
    db_workspace = models.Workspace(
        gid=str(uuid.uuid4()),
        **workspace.model_dump(exclude_unset=True)
    )
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    return db_workspace

# Stories
def get_stories(db: Session, task_gid: str):
    task = db.query(models.Task).filter(models.Task.gid == task_gid).first()
    if not task:
        return []
    return db.query(models.Story).filter(models.Story.task_id == task.id).all()

def create_story(db: Session, story: schemas.StoryCreate):
    db_story = models.Story(
        gid=str(uuid.uuid4()),
        **story.model_dump(exclude_unset=True)
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story
'''
        with open(f"{self.output_dir}/app/crud.py", "w") as f:
            f.write(code)
    
    def generate_routes(self):
        """Generate API routes"""
        code = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter()

# Task routes
@router.get("/tasks/{task_gid}", response_model=schemas.Task)
def get_task(task_gid: str, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_gid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)

@router.put("/tasks/{task_gid}", response_model=schemas.Task)
def update_task(task_gid: str, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.update_task(db, task_gid, task)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/tasks/{task_gid}")
def delete_task(task_gid: str, db: Session = Depends(get_db)):
    task = crud.delete_task(db, task_gid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

@router.get("/projects/{project_gid}/tasks", response_model=List[schemas.Task])
def get_tasks_for_project(project_gid: str, db: Session = Depends(get_db)):
    return crud.get_tasks_by_project(db, project_gid)

@router.get("/sections/{section_gid}/tasks", response_model=List[schemas.Task])
def get_tasks_for_section(section_gid: str, db: Session = Depends(get_db)):
    return crud.get_tasks_by_section(db, section_gid)

# Project routes
@router.get("/projects/{project_gid}", response_model=schemas.Project)
def get_project(project_gid: str, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_gid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, project)

@router.put("/projects/{project_gid}", response_model=schemas.Project)
def update_project(project_gid: str, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = crud.update_project(db, project_gid, project)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.delete("/projects/{project_gid}")
def delete_project(project_gid: str, db: Session = Depends(get_db)):
    project = crud.delete_project(db, project_gid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}

@router.get("/workspaces/{workspace_gid}/projects", response_model=List[schemas.Project])
def get_projects(workspace_gid: str, db: Session = Depends(get_db)):
    return crud.get_projects(db, workspace_gid)

# Section routes
@router.get("/projects/{project_gid}/sections", response_model=List[schemas.Section])
def get_sections(project_gid: str, db: Session = Depends(get_db)):
    return crud.get_sections(db, project_gid)

@router.post("/projects/{project_gid}/sections", response_model=schemas.Section)
def create_section(project_gid: str, section: schemas.SectionCreate, db: Session = Depends(get_db)):
    return crud.create_section(db, section)

@router.put("/sections/{section_gid}", response_model=schemas.Section)
def update_section(section_gid: str, section: schemas.SectionUpdate, db: Session = Depends(get_db)):
    db_section = crud.update_section(db, section_gid, section)
    if not db_section:
        raise HTTPException(status_code=404, detail="Section not found")
    return db_section

@router.delete("/sections/{section_gid}")
def delete_section(section_gid: str, db: Session = Depends(get_db)):
    section = crud.delete_section(db, section_gid)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return {"message": "Section deleted"}

# User routes
@router.get("/users/{user_gid}", response_model=schemas.User)
def get_user(user_gid: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_gid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/workspaces/{workspace_gid}/users", response_model=List[schemas.User])
def get_users(workspace_gid: str, db: Session = Depends(get_db)):
    return crud.get_users(db, workspace_gid)

@router.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

# Workspace routes
@router.get("/workspaces", response_model=List[schemas.Workspace])
def get_workspaces(db: Session = Depends(get_db)):
    return crud.get_workspaces(db)

@router.get("/workspaces/{workspace_gid}", response_model=schemas.Workspace)
def get_workspace(workspace_gid: str, db: Session = Depends(get_db)):
    workspace = crud.get_workspace(db, workspace_gid)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

@router.post("/workspaces", response_model=schemas.Workspace)
def create_workspace(workspace: schemas.WorkspaceCreate, db: Session = Depends(get_db)):
    return crud.create_workspace(db, workspace)

# Story routes
@router.get("/tasks/{task_gid}/stories", response_model=List[schemas.Story])
def get_stories(task_gid: str, db: Session = Depends(get_db)):
    return crud.get_stories(db, task_gid)

@router.post("/tasks/{task_gid}/stories", response_model=schemas.Story)
def create_story(task_gid: str, story: schemas.StoryCreate, db: Session = Depends(get_db)):
    return crud.create_story(db, story)
'''
        with open(f"{self.output_dir}/app/routes.py", "w") as f:
            f.write(code)
    
    def generate_main(self):
        """Generate main FastAPI app"""
        code = '''from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Asana Clone API", version="1.0.0")

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Asana Clone API"}
'''
        with open(f"{self.output_dir}/app/main.py", "w") as f:
            f.write(code)
        
        with open(f"{self.output_dir}/app/__init__.py", "w") as f:
            f.write("")
    
    def generate_requirements(self):
        """Generate requirements.txt"""
        requirements = """fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.6.1
alembic==1.13.1
pytest==8.0.0
pytest-asyncio==0.23.3
httpx==0.26.0
"""
        with open(f"{self.output_dir}/requirements.txt", "w") as f:
            f.write(requirements)
