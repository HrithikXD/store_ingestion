This API ingests three CSV files — Stores, Users, and Store-User Mapping — into a SQLite database using Django REST Framework. It validates each row, saves only valid data, and reports errors for invalid rows without stopping the entire process.

Core Approach
Read CSV files in chunks (10000 rows at a time, can be changed through settings.py) to handle large files efficiently
Perform row-level validation before database insertion
Use bulk insert operations to optimize database performance
Maintain a detailed error report for failed rows
Keep implementation simple and centralized in views.py

Validation Strategy
Each row is validated for:
Required fields → Ensures mandatory data is present
Data types → Latitude/longitude as float, user_type as integer
Format checks → Email validated via regex
Allowed values → user_type ∈ {1, 2, 3, 7}
Field length limits → username (≤150), email (≤254)
Uniqueness → Checked within file and database
Foreign key integrity → Mapping references must exist

Data Normalization
Lookup fields (e.g., city, region, brand) are:
Trimmed (strip()) and Lowercased - This avoids duplicate entries caused by case or spacing differences.

Failure Handling Strategy
Invalid rows are skipped, not rejected entirely
API returns:
- Row number
- Column name
- Error reason
     - Rationale: Ensures valid data is not blocked due to a few bad records.

Performance Optimization
Chunked processing → prevents memory overload
Preloaded reference sets → avoids repeated DB queries
bulk_create() → reduces DB calls drastically
Normalized lookups → prevents redundant inserts

Design Decisions & Tradeoffs
Database
SQLite
Lightweight, no setup
Structure
Single file (views.py)
Simplicity and clarity
File processing
pandas
Built-in chunking support

Conclusion
The system prioritizes - Data integrity through strict validation | Performance via chunking and bulk operations | Practical usability with partial success handling |
This results in a scalable, efficient, and easy-to-maintain ingestion pipeline suitable for real-world datasets.



Setup Overview

This project is a Django + Django REST Framework API using SQLite.
It ingests CSV files and stores validated data in the database.

1. Requirements Setup
Create requirements.txt
Stores all required Python packages for the project.
pip freeze > requirements.txt
Install dependencies
pip install -r requirements.txt

2. Setup on a New Machine
Prerequisite
Python 3.10+
Check version:
python --version

Step 1: Clone Repository
git clone <repo-url>
cd <project-folder>

Step 2: Create Virtual Environment
python -m venv venv
Activate:
Mac/Linux:
source venv/bin/activate
Windows:
venv\Scripts\activate

Step 3: Install Dependencies
pip install -r requirements.txt

Step 4: Setup Environment Variables
cp .env.example .env
Generate Django secret key:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
Add to .env:
SECRET_KEY=your_generated_key
DEBUG=True

Step 5: Run Migrations
python manage.py migrate
Creates SQLite database (db.sqlite3).

Step 6: Start Server
python manage.py runserver
Access at:
http://127.0.0.1:8000/

3. Testing the API
Upload Order (Important)
Stores
Users
Mapping

Using curl
curl -X POST http://localhost:8000/api/upload/stores/ -F "file=@stores.csv"
curl -X POST http://localhost:8000/api/upload/users/ -F "file=@users.csv"
curl -X POST http://localhost:8000/api/upload/mapping/ -F "file=@mapping.csv"

Using Postman
Method: POST
URL: /api/upload/<type>/
Body → form-data → file (File)


