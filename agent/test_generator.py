from typing import Dict
import os

class TestGenerator:
    def __init__(self, api_spec: Dict):
        self.api_spec = api_spec
        self.output_dir = "output/backend/tests"
        
    def generate_tests(self):
        """Generate pytest tests for all endpoints"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.generate_conftest()
        self.generate_task_tests()
        self.generate_project_tests()
        self.generate_section_tests()
        self.generate_user_tests()
        self.generate_workspace_tests()
        
    def generate_conftest(self):
        """Generate pytest configuration"""
        code = '''import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
'''
        with open(f"{self.output_dir}/conftest.py", "w") as f:
            f.write(code)
    
    def generate_task_tests(self):
        """Generate task endpoint tests"""
        code = '''import pytest

def test_create_task(client):
    response = client.post("/api/v1/tasks", json={
        "name": "Test Task",
        "notes": "Task description"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Task"
    assert "gid" in data

def test_get_task(client):
    # Create task first
    create_response = client.post("/api/v1/tasks", json={
        "name": "Test Task"
    })
    task_gid = create_response.json()["gid"]
    
    # Get task
    response = client.get(f"/api/v1/tasks/{task_gid}")
    assert response.status_code == 200
    assert response.json()["gid"] == task_gid

def test_get_task_not_found(client):
    response = client.get("/api/v1/tasks/nonexistent")
    assert response.status_code == 404

def test_update_task(client):
    # Create task
    create_response = client.post("/api/v1/tasks", json={
        "name": "Original Task"
    })
    task_gid = create_response.json()["gid"]
    
    # Update task
    response = client.put(f"/api/v1/tasks/{task_gid}", json={
        "name": "Updated Task",
        "completed": True
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Task"
    assert response.json()["completed"] == True

def test_delete_task(client):
    # Create task
    create_response = client.post("/api/v1/tasks", json={
        "name": "Task to Delete"
    })
    task_gid = create_response.json()["gid"]
    
    # Delete task
    response = client.delete(f"/api/v1/tasks/{task_gid}")
    assert response.status_code == 200
    
    # Verify deleted
    get_response = client.get(f"/api/v1/tasks/{task_gid}")
    assert get_response.status_code == 404

def test_create_task_with_empty_name(client):
    response = client.post("/api/v1/tasks", json={
        "name": ""
    })
    assert response.status_code == 200

def test_create_task_with_long_name(client):
    long_name = "A" * 300
    response = client.post("/api/v1/tasks", json={
        "name": long_name
    })
    assert response.status_code == 200

def test_create_task_with_special_characters(client):
    response = client.post("/api/v1/tasks", json={
        "name": "Task with special chars: @#$%^&*()"
    })
    assert response.status_code == 200

def test_update_task_completed_flag(client):
    create_response = client.post("/api/v1/tasks", json={
        "name": "Task"
    })
    task_gid = create_response.json()["gid"]
    
    # Test completed True
    response = client.put(f"/api/v1/tasks/{task_gid}", json={
        "completed": True
    })
    assert response.json()["completed"] == True
    
    # Test completed False
    response = client.put(f"/api/v1/tasks/{task_gid}", json={
        "completed": False
    })
    assert response.json()["completed"] == False
'''
        with open(f"{self.output_dir}/test_tasks.py", "w") as f:
            f.write(code)
    
    def generate_project_tests(self):
        """Generate project endpoint tests"""
        code = '''import pytest

def test_create_project(client):
    response = client.post("/api/v1/projects", json={
        "name": "Test Project",
        "notes": "Project notes"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert "gid" in data

def test_get_project(client):
    create_response = client.post("/api/v1/projects", json={
        "name": "Test Project"
    })
    project_gid = create_response.json()["gid"]
    
    response = client.get(f"/api/v1/projects/{project_gid}")
    assert response.status_code == 200
    assert response.json()["gid"] == project_gid

def test_update_project(client):
    create_response = client.post("/api/v1/projects", json={
        "name": "Original Project"
    })
    project_gid = create_response.json()["gid"]
    
    response = client.put(f"/api/v1/projects/{project_gid}", json={
        "name": "Updated Project"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project"

def test_delete_project(client):
    create_response = client.post("/api/v1/projects", json={
        "name": "Project to Delete"
    })
    project_gid = create_response.json()["gid"]
    
    response = client.delete(f"/api/v1/projects/{project_gid}")
    assert response.status_code == 200
    
    get_response = client.get(f"/api/v1/projects/{project_gid}")
    assert get_response.status_code == 404

def test_get_project_not_found(client):
    response = client.get("/api/v1/projects/nonexistent")
    assert response.status_code == 404

def test_create_project_with_empty_name(client):
    response = client.post("/api/v1/projects", json={
        "name": ""
    })
    assert response.status_code == 200

def test_project_archived_flag(client):
    create_response = client.post("/api/v1/projects", json={
        "name": "Project",
        "archived": False
    })
    project_gid = create_response.json()["gid"]
    
    response = client.put(f"/api/v1/projects/{project_gid}", json={
        "archived": True
    })
    assert response.json()["archived"] == True
'''
        with open(f"{self.output_dir}/test_projects.py", "w") as f:
            f.write(code)
    
    def generate_section_tests(self):
        """Generate section endpoint tests"""
        code = '''import pytest

def test_create_section(client):
    # Create project first
    project_response = client.post("/api/v1/projects", json={
        "name": "Test Project"
    })
    project_gid = project_response.json()["gid"]
    
    response = client.post(f"/api/v1/projects/{project_gid}/sections", json={
        "name": "Test Section",
        "project": project_gid
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Test Section"

def test_get_sections(client):
    project_response = client.post("/api/v1/projects", json={
        "name": "Test Project"
    })
    project_gid = project_response.json()["gid"]
    
    client.post(f"/api/v1/projects/{project_gid}/sections", json={
        "name": "Section 1",
        "project": project_gid
    })
    client.post(f"/api/v1/projects/{project_gid}/sections", json={
        "name": "Section 2",
        "project": project_gid
    })
    
    response = client.get(f"/api/v1/projects/{project_gid}/sections")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_update_section(client):
    project_response = client.post("/api/v1/projects", json={
        "name": "Test Project"
    })
    project_gid = project_response.json()["gid"]
    
    section_response = client.post(f"/api/v1/projects/{project_gid}/sections", json={
        "name": "Original Section",
        "project": project_gid
    })
    section_gid = section_response.json()["gid"]
    
    response = client.put(f"/api/v1/sections/{section_gid}", json={
        "name": "Updated Section"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Section"

def test_delete_section(client):
    project_response = client.post("/api/v1/projects", json={
        "name": "Test Project"
    })
    project_gid = project_response.json()["gid"]
    
    section_response = client.post(f"/api/v1/projects/{project_gid}/sections", json={
        "name": "Section to Delete",
        "project": project_gid
    })
    section_gid = section_response.json()["gid"]
    
    response = client.delete(f"/api/v1/sections/{section_gid}")
    assert response.status_code == 200
'''
        with open(f"{self.output_dir}/test_sections.py", "w") as f:
            f.write(code)
    
    def generate_user_tests(self):
        """Generate user endpoint tests"""
        code = '''import pytest

def test_create_user(client):
    response = client.post("/api/v1/users", json={
        "name": "Test User",
        "email": "test@example.com"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"
    assert response.json()["email"] == "test@example.com"

def test_get_user(client):
    create_response = client.post("/api/v1/users", json={
        "name": "Test User",
        "email": "test@example.com"
    })
    user_gid = create_response.json()["gid"]
    
    response = client.get(f"/api/v1/users/{user_gid}")
    assert response.status_code == 200
    assert response.json()["gid"] == user_gid

def test_get_user_not_found(client):
    response = client.get("/api/v1/users/nonexistent")
    assert response.status_code == 404

def test_create_user_with_invalid_email(client):
    response = client.post("/api/v1/users", json={
        "name": "Test User",
        "email": "invalid-email"
    })
    assert response.status_code == 200
'''
        with open(f"{self.output_dir}/test_users.py", "w") as f:
            f.write(code)
    
    def generate_workspace_tests(self):
        """Generate workspace endpoint tests"""
        code = '''import pytest

def test_create_workspace(client):
    response = client.post("/api/v1/workspaces", json={
        "name": "Test Workspace"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Test Workspace"

def test_get_workspaces(client):
    client.post("/api/v1/workspaces", json={"name": "Workspace 1"})
    client.post("/api/v1/workspaces", json={"name": "Workspace 2"})
    
    response = client.get("/api/v1/workspaces")
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_get_workspace(client):
    create_response = client.post("/api/v1/workspaces", json={
        "name": "Test Workspace"
    })
    workspace_gid = create_response.json()["gid"]
    
    response = client.get(f"/api/v1/workspaces/{workspace_gid}")
    assert response.status_code == 200
    assert response.json()["gid"] == workspace_gid

def test_get_workspace_not_found(client):
    response = client.get("/api/v1/workspaces/nonexistent")
    assert response.status_code == 404
'''
        with open(f"{self.output_dir}/test_workspaces.py", "w") as f:
            f.write(code)
        
        with open(f"{self.output_dir}/__init__.py", "w") as f:
            f.write("")
