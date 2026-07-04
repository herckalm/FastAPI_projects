Secure Hero Missions API
A production-oriented backend application built with FastAPI for a superhero organization, managing users, heroes, and missions with robust data validation, JWT security, and automated tests.

Developed as part of the Coding Factory (Center of Education and Lifelong Learning - Athens University of Economics and Business).

Tech Stack & Architecture
FastAPI: For creating REST endpoints and scalable modular routing.

SQLModel & SQLite: For seamless ORM database management and relational mappings.

Pytest: For executing automated test cases against a clean in-memory database environment.

JWT (JSON Web Tokens): For secure registration, login flow, and role-based authentication (Users/Admins).

uv: Modern, fast Python package manager for reliable environment and dependency management.
    
    
Installation & Execution Guide on Ubuntu
Follow these terminal steps to set up and run the application locally:

1. Install uv (If not already installed)
Bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
2. Navigate to the Project Root Folder
Bash
cd ~/Desktop/aueb/FastAPI_projects/hero_api
3. Create a Virtual Environment & Install Dependencies
Bash
uv venv --python 3.11 --cache-dir .uv-cache
source .venv/bin/activate
uv pip install -r requirements.txt --cache-dir .uv-cache
4. Run Automated Test Cases
Bash
python -m pytest tests/
5. Start the Development Uvicorn Server
Bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Once the server is running, visit http://localhost:8000/docs in your browser to interact with the full API via the Swagger UI.

Business Rules & Access Controls
Roles & Endpoint Privileges:

Public Access: All global GET endpoints (Listing/Retrieving heroes and missions) are accessible publicly without requiring a token.

Authenticated Users: Registered users can log in to generate an access token, which grants them permission to create or update (PATCH) heroes and missions.

Admins Only: Complete deletion (DELETE) operations for both heroes and missions are strictly restricted to administrators.

Data Constraints & Business Validations:

Heroes: Name and power fields enforce a minimum length of 3 characters. The level attribute must strictly fall within the range of 1 to 100.

Missions: The title must contain at least 5 characters, and the difficulty must be an integer score between 1 and 10.

Hero Deletion Safeguard: The system will block any attempts to delete a superhero who currently has active (uncompleted) missions assigned to them.

Mission Assignment Safeguard: Creating or modifying a mission requires a valid hero_id that corresponds to an existing hero in the database.
