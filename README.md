# TaskAPI

## Features
- CRUD operations for tasks (title, description, is_completed)
- SQLite database
- Filter by completion status

## Requirements
- Python 3.7+
- FastAPI
- SQLAlchemy
- Uvicorn

 ## Setup

```bash
git clone https://github.com/SupriyaS26/TaskAPI.git
cd task-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
