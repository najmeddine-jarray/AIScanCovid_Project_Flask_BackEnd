# run.py
import os
from app import app  # Import from the app package

if __name__ == '__main__':
    print("Starting AI ScanCovid Server...")
    app.run()
