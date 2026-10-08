"""
InsightFlow - Master Startup & Launcher Script (run.py)
1. Checks and installs any missing packages.
2. Populates sample e-commerce dataset if not present.
3. Triggers PySpark & NLP Big Data ingestion into SQLite.
4. Boots the Flask web server on http://127.0.0.1:5000 with a clickable local URL.
"""

import os
import sys
import subprocess
import webbrowser

REQUIRED_PACKAGES = [
    "pyspark",
    "pandas",
    "numpy",
    "flask",
    "vaderSentiment",
    "scikit-learn"
]

def check_and_install_dependencies():
    """Verifies all required packages are installed."""
    print("=" * 65)
    print(" [1/4] Checking Python Dependencies for InsightFlow...")
    print("=" * 65)
    
    missing_packages = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            missing_packages.append(pkg)

    if missing_packages:
        print(f"Missing packages detected: {missing_packages}. Installing now...")
        cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print("Warning: pip install returned non-zero code. Continuing startup...")
    else:
        print("✓ All required Python packages are already installed.")

def setup_data_and_database():
    """Ensures sample review data and SQLite database are initialized."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_csv = os.path.join(base_dir, "data_input", "sample_reviews.csv")
    db_file = os.path.join(base_dir, "database", "insightflow.db")
    
    import generate_data
    import spark_processor

    print("\n" + "=" * 65)
    print(" [2/4] Verifying Seed Dataset...")
    print("=" * 65)
    if not os.path.exists(sample_csv):
        print(f"Generating realistic e-commerce review dataset at {sample_csv}...")
        generate_data.generate_sample_dataset(sample_csv)
    else:
        print(f"✓ Found existing sample dataset: {sample_csv}")

    print("\n" + "=" * 65)
    print(" [3/4] Ingesting & Extracting Root-Cause Insights (PySpark & NLP)...")
    print("=" * 65)
    spark_processor.process_file(sample_csv)
    print(f"✓ Big Data Pipeline completed. Database ready at {db_file}")

def start_flask_server():
    """Boots the Flask web server."""
    print("\n" + "=" * 65)
    print(" [4/4] Launching InsightFlow Web Dashboard...")
    print("=" * 65)
    url = "http://127.0.0.1:5000"
    print("\n🚀 InsightFlow Full-Stack Engine is now LIVE!")
    print(f"👉 Access the dashboard at: {url}")
    print("👉 Press Ctrl+C in this console to stop the server.\n")

    # Import and run app
    from app import app
    app.run(host="127.0.0.1", port=5000, debug=False)

if __name__ == "__main__":
    check_and_install_dependencies()
    setup_data_and_database()
    start_flask_server()
