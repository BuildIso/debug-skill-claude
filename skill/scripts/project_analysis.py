import os
import json
from pathlib import Path

IGNORED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    "dist", "build", ".idea", ".vscode", "coverage"
}

IMPORTANT_FILES = {
    "main.py": 100,
    "app.py": 95,
    "index.py": 90,
    "server.py": 90,
    "manage.py": 85,
    "package.json": 85,
    "pyproject.toml": 80,
    "requirements.txt": 75,
    "Dockerfile": 70,
    "docker-compose.yml": 70,
    ".env.example": 65,
    "README.md": 50
}

IMPORTANT_DIRS = {
    "src": 30,
    "app": 30,
    "core": 25,
    "api": 25,
    "services": 20,
    "config": 20,
    "tests": 10
}

def should_ignore(path):
    return any(part in IGNORED_DIRS for part in path.parts)

def calculate_priority(path, root):
    score = 0
    name = path.name.lower()

    score += IMPORTANT_FILES.get(name, 0)

    for part in path.relative_to(root).parts[:-1]:
        score += IMPORTANT_DIRS.get(part.lower(), 0)

    if path.suffix in {".py", ".js", ".ts", ".jsx", ".tsx"}:
        score += 15

    if path.suffix in {".json", ".yaml", ".yml", ".toml"}:
        score += 5

    return score

def scan_project(project_path):
    root = Path(project_path).resolve()

    if not root.is_dir():
        raise ValueError("Invalid project directory")

    files = []

    for current_root, dirs, filenames in os.walk(root):
        dirs[:] = [
            directory for directory in dirs
            if directory not in IGNORED_DIRS
        ]

        current = Path(current_root)

        for filename in filenames:
            file_path = current / filename

            if should_ignore(file_path.relative_to(root)):
                continue

            priority = calculate_priority(file_path, root)

            files.append({
                "file": str(file_path.relative_to(root)),
                "priority": priority
            })

    files.sort(key=lambda item: item["priority"], reverse=True)

    return {
        "project": root.name,
        "total_files": len(files),
        "priority_files": files[:30],
        "all_files": files
    }

def main():
    project_path = input("Project path: ").strip()

    try:
        results = scan_project(project_path)

        output_path = Path(project_path).resolve() / "project_scan.json"

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(results, file, indent=4, ensure_ascii=False)

        print(f"Scan completed: {results['total_files']} files")
        print(f"Priority report: {output_path}")

        for item in results["priority_files"]:
            print(f"[{item['priority']}] {item['file']}")

    except (ValueError, OSError) as error:
        print(f"Scan failed: {error}")

if __name__ == "__main__":
    main()
  
