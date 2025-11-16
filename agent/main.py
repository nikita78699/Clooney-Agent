import yaml
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.scraper import AsanaAPIScraper
from agent.analyzer import APIAnalyzer
from agent.generator import CodeGenerator
from agent.test_generator import TestGenerator
from agent.docker_generator import DockerGenerator

def main():
    print("🚀 Starting Clooney Agent - Backend Replication for Asana")
    print("=" * 60)
    
    # Step 1: Scrape API documentation
    print("\n[1/6] Scraping Asana API documentation...")
    scraper = AsanaAPIScraper()
    api_spec = scraper.scrape_api_docs()
    print(f"✓ Found {len(api_spec['endpoints'])} endpoints")
    print(f"✓ Found {len(api_spec['schemas'])} schemas")
    
    # Step 2: Analyze API structure
    print("\n[2/6] Analyzing API structure and generating database schema...")
    analyzer = APIAnalyzer(api_spec)
    db_schema = analyzer.analyze_schema()
    print(f"✓ Generated schema for {len(db_schema)} tables")
    
    # Step 3: Generate OpenAPI spec
    print("\n[3/6] Generating OpenAPI specification...")
    openapi_spec = analyzer.generate_openapi_spec()
    os.makedirs("output/backend", exist_ok=True)
    with open("output/backend/api.yml", "w") as f:
        yaml.dump(openapi_spec, f, sort_keys=False)
    print("✓ OpenAPI spec saved to output/backend/api.yml")
    
    # Step 4: Generate FastAPI code
    print("\n[4/6] Generating FastAPI application code...")
    generator = CodeGenerator(db_schema, api_spec)
    generator.generate_all()
    print("✓ Generated models, schemas, CRUD operations, and routes")
    print("✓ Generated main.py and requirements.txt")
    
    # Step 5: Generate tests
    print("\n[5/6] Generating pytest test cases...")
    test_gen = TestGenerator(api_spec)
    test_gen.generate_tests()
    print("✓ Generated comprehensive test suites")
    
    # Step 6: Generate Docker setup
    print("\n[6/6] Generating Docker configuration...")
    docker_gen = DockerGenerator()
    docker_gen.generate_dockerfile()
    docker_gen.generate_docker_compose()
    docker_gen.generate_alembic_config()
    docker_gen.generate_schema_sql(db_schema)
    print("✓ Generated Dockerfile and docker-compose.yml")
    print("✓ Generated Alembic migration setup")
    print("✓ Generated schema.sql")
    
    print("\n" + "=" * 60)
    print("✅ Backend replication complete!")
    print("\nGenerated files:")
    print("  📁 output/backend/")
    print("     ├── app/")
    print("     │   ├── main.py")
    print("     │   ├── models.py")
    print("     │   ├── schemas.py")
    print("     │   ├── crud.py")
    print("     │   ├── routes.py")
    print("     │   └── database.py")
    print("     ├── tests/")
    print("     │   ├── test_tasks.py")
    print("     │   ├── test_projects.py")
    print("     │   ├── test_sections.py")
    print("     │   ├── test_users.py")
    print("     │   └── test_workspaces.py")
    print("     ├── alembic/")
    print("     ├── api.yml")
    print("     ├── schema.sql")
    print("     ├── Dockerfile")
    print("     ├── docker-compose.yml")
    print("     └── requirements.txt")
    print("\n💡 Next steps:")
    print("  1. cd output/backend")
    print("  2. docker-compose up --build")
    print("  3. pytest tests/")

if __name__ == "__main__":
    main()
