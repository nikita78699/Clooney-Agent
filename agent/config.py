import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/asana_clone")

ASANA_API_DOCS_URL = "https://developers.asana.com/docs"

FOCUS_ENDPOINTS = [
    "tasks",
    "projects", 
    "sections",
    "users",
    "workspaces",
    "stories"
]
