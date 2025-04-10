# run.py
import os
from app import app  # Import from the app package

if __name__ == '__main__':
    print("Starting AI ScanCovid Server...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
