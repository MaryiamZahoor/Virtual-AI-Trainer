"""
setup_project.py
================
Creates project folder structure and Python __init__.py files.
"""

import os
from pathlib import Path


class ProjectSetup:
    """Simple project setup utility"""
    
    def __init__(self, root_path: str = "."):
        """Initialize with root directory"""
        self.root_path = Path(root_path)
        
        # All folders to create
        self.folders = [
            # Backend
            "backend",
            "backend/app",
            "backend/app/api",
            "backend/app/models",
            "backend/app/services",
            "backend/app/ml",
            "backend/app/utils",
            "backend/tests",
            
            # Frontend
            "frontend",
            "frontend/js",
            "frontend/models",
            "frontend/assets",
            "frontend/assets/exercise-references",
            "frontend/assets/icons",
            
            # Other
            ".github/workflows",
            "docs",
        ]
        
        # Python packages (need __init__.py)
        self.python_packages = [
            "backend/app",
            "backend/app/api",
            "backend/app/models",
            "backend/app/services",
            "backend/app/ml",
            "backend/app/utils",
            "backend/tests",
        ]
    
    def create_folders(self) -> None:
        """Create all required folders"""
        print("\n📁 Creating folders...\n")
        
        for folder in self.folders:
            folder_path = self.root_path / folder
            
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ {folder}")
            except Exception as e:
                print(f"  ❌ {folder} - Error: {e}")
        
        print("\n✅ All folders created!\n")
    
    def create_init_files(self) -> None:
        """Create __init__.py files in Python packages"""
        print("🐍 Creating __init__.py files...\n")
        
        for package in self.python_packages:
            init_file = self.root_path / package / "__init__.py"
            
            try:
                # Create empty file
                init_file.touch(exist_ok=True)
                print(f"  ✅ {package}/__init__.py")
            except Exception as e:
                print(f"  ❌ {package}/__init__.py - Error: {e}")
        
        print("\n✅ All __init__.py files created!\n")
    
    def run(self) -> None:
        """Run the setup"""
        print("=" * 50)
        print("🚀 VIRTUAL AI TRAINER - PROJECT SETUP")
        print("=" * 50)
        
        self.create_folders()
        self.create_init_files()
        
        print("=" * 50)
        print("✅ PROJECT STRUCTURE READY!")
        print("=" * 50)
        

# Entry point
if __name__ == "__main__":
    setup = ProjectSetup(root_path=".")
    setup.run()