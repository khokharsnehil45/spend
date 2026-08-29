"""
Vercel Serverless Function entry point for SPEND FastAPI.
"""
from server import app

# Ensure database is initialized on serverless cold start
import db
db.init_db()
