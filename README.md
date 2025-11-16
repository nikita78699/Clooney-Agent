# Clooney - Backend Replication Agent

An agentic system that automatically replicates web application backends by analyzing API documentation and generating production-ready FastAPI code.

## Overview

This agent replicates Asana's backend APIs for **Home, Projects, and Tasks** pages, generating:
- ✅ FastAPI application with complete CRUD operations
- ✅ PostgreSQL database schema with Alembic migrations
- ✅ OpenAPI specification (api.yml)
- ✅ Exhaustive pytest test suites
- ✅ Docker setup (Dockerfile + docker-compose.yml)

## Features Replicated

### Tasks
- Task CRUD operations
- Title, description, due date, assignee
- Completed flag
- Subtasks support
- Task comments (stories)

### Projects
- Project management
- Sections within projects
- Tasks organized in sections
- Reordering and moving tasks

### Users & Workspaces
- User management
- Workspace support
- Assignees and collaborators

## Prerequisites

Before running this project, ensure you have:

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: `python --version` or `python3 --version`

2. **Docker Desktop or Rancher Desktop** (for Docker setup)
   - Docker Desktop: https://www.docker.com/products/docker-desktop
   - Rancher Desktop: https://rancherdesktop.io/ (alternative)
   - Verify: `docker --version`
   - **Important:** Make sure Docker/Rancher Desktop application is running before using docker-compose

3. **Git** (optional, to clone repository)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If `pip` command not found, use:
- Windows: `python -m pip install -r requirements.txt`
- Mac/Linux: `python3 -m pip install -r requirements.txt`

### 2. Configure Environment (Optional)

Copy `.env.template` to `.env` if you want to customize database settings:
```bash
cp .env.template .env
```

**Note:** The agent uses pre-configured Asana API documentation structure, so LLM API keys are optional. The agent will work out of the box without requiring external API keys.

### 3. Run the Agent

```bash
python agent/main.py
```

The agent will generate the complete backend in `output/backend/`.

## Running the Generated Backend

### Quick Start (Docker - Recommended)

If you just want to run the pre-generated backend **without running the agent**:

```bash
# 1. Navigate to the generated backend folder
cd output/backend

# 2. Start with Docker
docker-compose up --build
```

API will be available at: `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

**Note:** No need to install Python dependencies or PostgreSQL when using Docker. Everything runs in containers.

### Full Flow (Generate + Run)

To regenerate the backend from scratch and then run it:

```bash
# 1. Install agent dependencies (requires Python)
pip install -r requirements.txt

# 2. Run the agent to generate backend
python agent/main.py

# 3. Navigate to generated backend
cd output/backend

# 4. Start with Docker
docker-compose up --build
```

**Troubleshooting:**
- If you see "Cannot connect to the Docker daemon": Start Docker Desktop application and wait for it to fully launch
- Verify Docker is running: `docker ps`

### Without Docker

1. Install PostgreSQL locally
2. Create database:
   ```bash
   createdb asana_clone
   ```
3. Install dependencies:
   ```bash
   cd output/backend
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   alembic upgrade head
   ```
5. Start server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Running Tests

**Prerequisites:** Docker must be running (`docker-compose up -d`)

```bash
cd output/backend

# Windows
pytest tests/ -v

#Mac/Linux
python3 -m pytest tests/ -v
```

**Expected Output:** 28 tests pass successfully

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

OpenAPI specification: `output/backend/api.yml`

## Project Structure

```
Clooney-Agent/
├── agent/                      # Agent source code
│   ├── main.py                # Entry point
│   ├── scraper.py             # API documentation scraper
│   ├── analyzer.py            # Schema analyzer
│   ├── generator.py           # FastAPI code generator
│   ├── test_generator.py     # Test generator
│   └── docker_generator.py   # Docker setup generator
├── output/
│   └── backend/               # Generated backend (created after running agent)
│       ├── app/
│       │   ├── main.py       # FastAPI app
│       │   ├── models.py     # SQLAlchemy models
│       │   ├── schemas.py    # Pydantic schemas
│       │   ├── crud.py       # CRUD operations
│       │   ├── routes.py     # API routes
│       │   └── database.py   # DB configuration
│       ├── tests/            # Pytest test suites
│       ├── alembic/          # Database migrations
│       ├── api.yml           # OpenAPI specification
│       ├── schema.sql        # Database schema
│       ├── Dockerfile
│       └── docker-compose.yml
├── requirements.txt          # Agent dependencies
├── .env.template
└── README.md
```

## API Endpoints

### Tasks
- `GET /api/v1/tasks/{task_gid}` - Get task
- `POST /api/v1/tasks` - Create task
- `PUT /api/v1/tasks/{task_gid}` - Update task
- `DELETE /api/v1/tasks/{task_gid}` - Delete task
- `GET /api/v1/projects/{project_gid}/tasks` - Get tasks by project
- `GET /api/v1/sections/{section_gid}/tasks` - Get tasks by section

### Projects
- `GET /api/v1/projects/{project_gid}` - Get project
- `POST /api/v1/projects` - Create project
- `PUT /api/v1/projects/{project_gid}` - Update project
- `DELETE /api/v1/projects/{project_gid}` - Delete project
- `GET /api/v1/workspaces/{workspace_gid}/projects` - Get projects

### Sections
- `GET /api/v1/projects/{project_gid}/sections` - Get sections
- `POST /api/v1/projects/{project_gid}/sections` - Create section
- `PUT /api/v1/sections/{section_gid}` - Update section
- `DELETE /api/v1/sections/{section_gid}` - Delete section

### Users & Workspaces
- `GET /api/v1/users/{user_gid}` - Get user
- `GET /api/v1/workspaces/{workspace_gid}/users` - Get users
- `GET /api/v1/workspaces` - Get workspaces
- `POST /api/v1/tasks/{task_gid}/stories` - Add comment

## Test Coverage

The test suite includes:
- ✅ Basic CRUD operations
- ✅ Edge cases (empty strings, long inputs, special characters)
- ✅ 404 error handling
- ✅ Boolean flag toggling
- ✅ Relationship testing (tasks in projects/sections)

## Database Schema

Generated `schema.sql` includes:
- Tasks table with foreign keys
- Projects table
- Sections table
- Users table
- Workspaces table
- Stories (comments) table
- Proper timestamps and constraints

## Technologies Used

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Database
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Pytest** - Testing framework
- **Docker** - Containerization

## Notes

- This is an **agent** that generates code, not a manual implementation
- The agent focuses on API structure and business logic replication
- Database schema inferred from Asana API documentation
- Generated code follows FastAPI best practices
- All endpoints include proper error handling

## Author

This project was documented and managed by Nikita Singhal.

For any queries, feel free to reach out at: nikita9084243020@gmail.com




