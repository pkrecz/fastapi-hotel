SELECT 'CREATE DATABASE fastapi_hotel_db' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'fastapi_hotel_db')\gexec
