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
