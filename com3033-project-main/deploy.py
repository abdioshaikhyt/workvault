#!/usr/bin/env python3
import subprocess
import time
import sys
import argparse
from pathlib import Path
import re

def run_command(cmd):
    """Run a shell command and print output"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=False)
        print("✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        return False

def main():
    print("🚀 Starting WorkVault deployment...")

    # Parse command line argument for .env file for web domain
    parser = argparse.ArgumentParser(description="Deploy frontend with custom URL_FOR_PW")
    parser.add_argument("-n", "--name", required=True, help="Full URL to set as URL_FOR_PW (e.g., http://localhost/ or https://group11-web.com3033.csee-systems.com/)")
    args = parser.parse_args()

    url_for_pw = args.name

    env_path = Path(".env")
    if not env_path.exists():
        print(".env file not found!")
        sys.exit(1)

    contents = env_path.read_text()

    if "URL_FOR_PW=" in contents:
        new_contents = re.sub(r'URL_FOR_PW=.*', f'URL_FOR_PW={url_for_pw}/', contents)
   
    env_path.write_text(new_contents)
    print(f"Set URL_FOR_PW to {url_for_pw}/ in .env")
    
    # 1. Start services
    print("\n1. Building and starting Docker Compose...")
    if not run_command(["docker", "compose", "up", "--build", "-d"]):
        sys.exit(1)
    
    # 2. Wait 120 seconds for services to be ready
    print("\n⏳ Waiting 120 seconds for services to initialize...")
    time.sleep(120)
    
    # 3. Run migrations
    print("\n2. Running database migrations...")
    services = [
        "backendauth_app",
        "backend1_app", 
        "backend2_app",
        "backend3_app",
        "backend4_app"
    ]
    
    for service in services:
        print(f"\nMigrating {service}...")
        cmd = ["docker", "compose", "exec", service, "python", "manage.py", "migrate"]
        if not run_command(cmd):
            print(f"⚠️ Migration failed for {service}, continuing...")
    
    # 4. Rebuild elasticsearch index
    print("\n3. Rebuilding search index...")
    run_command([
        "docker", "exec", "-it", "com3033-project-backend2_app-1", 
        "bash", "-c", "python manage.py search_index --rebuild -f"
    ])
    
    # 5. Create superuser
    print("\n4. Creating superuser...")
    run_command([
        "docker", "compose", "exec", "backendauth_app", 
        "bash", "-c", 
        "DJANGO_SUPERUSER_USERNAME=workvault DJANGO_SUPERUSER_PASSWORD=workvault DJANGO_SUPERUSER_EMAIL='workvaultcontact@gmail.com' python manage.py createsuperuser --noinput"
    ])

    # 6. Run courses spider (web scraping)
    print("\n5. Running courses web scraper...")
    run_command([
        "docker", "compose", "exec", "backend4_app", 
        "python", "/code/backend4/backend4app/run_courses_spider_script.py"
    ])
    
    print("\n🎉 Deployment complete! Visit http://localhost in browser. Check your services:")
    print("   docker compose ps")
    print("   docker compose logs -f")

if __name__ == "__main__":
    main()