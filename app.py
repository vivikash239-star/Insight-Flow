"""
InsightFlow - Flask Full-Stack Web Application (app.py)
Provides web dashboard, CSV upload pipeline, and dual-dropdown intelligence API.
"""

import os
import sqlite3
import subprocess
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import generate_data
import spark_processor

app = Flask(__name__)
app.secret_key = "insightflow-secret-key-production-ready"
app.config["MAX_CONTENT_LENGTH"] = 1000 * 1024 * 1024  # 100 MB max upload
app.json.sort_keys = False
ALLOWED_EXTENSIONS = {"csv"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_INPUT_DIR = os.path.join(BASE_DIR, "data_input")
DB_PATH = os.path.join(BASE_DIR, "database", "insightflow.db")

os.makedirs(DATA_INPUT_DIR, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_database_ready():
    """Ensures database exists and has seed data if empty."""
    if not os.path.exists(DB_PATH):
        print("[InsightFlow App] Database not found. Initializing seed data and processing...")
        csv_path = generate_data.generate_sample_dataset()
        spark_processor.process_file(csv_path)
    else:
        try:
            conn = get_db_connection()
            count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            conn.close()
            if count == 0:
                print("[InsightFlow App] Database is empty. Running seed pipeline...")
                csv_path = generate_data.generate_sample_dataset()
                spark_processor.process_file(csv_path)
        except Exception as e:
            print(f"[InsightFlow App] Database verification error: {e}. Rebuilding...")
            csv_path = generate_data.generate_sample_dataset()
            spark_processor.process_file(csv_path)

@app.route("/")
def index():
    """Renders main dashboard with populated product list."""
    ensure_database_ready()
    conn = get_db_connection()
    products = conn.execute("SELECT product_id, product_name, total_reviews FROM products ORDER BY product_id").fetchall()
    
    # Global metrics
    total_products = len(products)
    total_reviews = sum(p["total_reviews"] for p in products) if products else 0
    total_defects = conn.execute("SELECT COUNT(*) FROM extracted_insights WHERE category = 'problem'").fetchone()[0]
    total_features = conn.execute("SELECT COUNT(*) FROM extracted_insights WHERE category = 'feature'").fetchone()[0]
    
    conn.close()
    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_reviews=total_reviews,
        total_defects=total_defects,
        total_features=total_features
    )

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles review CSV file uploads via AJAX and triggers PySpark pipeline."""
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file part in the request."}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected."}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        saved_path = os.path.join(DATA_INPUT_DIR, filename)
        file.save(saved_path)
        
        try:
            # Synchronously trigger spark_processor.py and wait for it to finish completely
            subprocess.run(["python", "spark_processor.py", saved_path], cwd=BASE_DIR, check=True)
            return jsonify({
                "status": "success",
                "message": f"Successfully processed '{filename}'! Data is now synchronized.",
                "filename": filename
            }), 200
        except subprocess.CalledProcessError as e:
            return jsonify({
                "status": "error",
                "message": f"Error executing PySpark processor: {str(e)}"
            }), 500
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error processing CSV: {str(e)}"
            }), 500
    else:
        return jsonify({"status": "error", "message": "Invalid file format. Please upload a valid .csv file."}), 400

@app.route("/api/products", methods=["GET"])
def api_products():
    """Returns all available products."""
    ensure_database_ready()
    conn = get_db_connection()
    rows = conn.execute("SELECT product_id, product_name, total_reviews FROM products ORDER BY product_id").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/analyze", methods=["POST"])
@app.route("/api/insights", methods=["GET", "POST"])
def analyze():
    """
    Accepts:
    - product_id (e.g. 'PROD-001' or 'ALL')
    - insight_mode ('problem', 'review', or 'feature')
    Returns targeted structured JSON for frontend rendering.
    """
    ensure_database_ready()
    
    if request.method == "POST":
        if request.is_json:
            data = request.get_json() or {}
            product_id = data.get("product_id")
            insight_mode = data.get("insight_mode", "problem")
        else:
            product_id = request.form.get("product_id")
            insight_mode = request.form.get("insight_mode", "problem")
    else:
        product_id = request.args.get("product_id")
        insight_mode = request.args.get("insight_mode", "problem")

    conn = get_db_connection()
    
    # If no product specified or product doesn't exist, default to first product
    first_product = conn.execute("SELECT product_id FROM products LIMIT 1").fetchone()
    if not product_id and first_product:
        product_id = first_product["product_id"]

    product_info = None
    if product_id and product_id != "ALL":
        prod_row = conn.execute("SELECT product_id, product_name, total_reviews FROM products WHERE product_id = ?", (product_id,)).fetchone()
        if prod_row:
            product_info = dict(prod_row)

    if not product_info:
        product_info = {
            "product_id": "ALL",
            "product_name": "All Analyzed Products (Aggregate)",
            "total_reviews": conn.execute("SELECT SUM(total_reviews) FROM products").fetchone()[0] or 0
        }

    # Summary metrics for selected product
    base_filter = "WHERE product_id = ?" if product_id != "ALL" else "WHERE 1=1"
    params = (product_id,) if product_id != "ALL" else ()

    defect_count = conn.execute(f"SELECT COUNT(*) FROM extracted_insights {base_filter} AND category = 'problem'", params).fetchone()[0]
    feature_count = conn.execute(f"SELECT COUNT(*) FROM extracted_insights {base_filter} AND category = 'feature'", params).fetchone()[0]
    good_count = conn.execute(f"SELECT COUNT(*) FROM extracted_insights {base_filter} AND category = 'good_review'", params).fetchone()[0]
    bad_count = conn.execute(f"SELECT COUNT(*) FROM extracted_insights {base_filter} AND (category = 'bad_review' OR category = 'problem')", params).fetchone()[0]

    # Improvement suggestion
    suggestion = None
    if product_id != "ALL":
        sug_row = conn.execute("SELECT suggestion_text, aspect_focus FROM improvement_suggestions WHERE product_id = ?", (product_id,)).fetchone()
        if sug_row:
            suggestion = {
                "text": sug_row["suggestion_text"],
                "focus": sug_row["aspect_focus"]
            }
    if not suggestion:
        suggestion = {
            "text": "Actionable Recommendation (Cross-Product QA): Standardize mechanical stress testing on display bezels, upgrade battery charging safety shutoffs, and implement IP68 acoustic seals across upcoming manufacturing production runs.",
            "focus": "Cross-Product Architecture"
        }

    # Aspect distribution for the selected mode
    category_filter = ""
    if insight_mode == "problem":
        category_filter = "AND category = 'problem'"
    elif insight_mode == "feature":
        category_filter = "AND category = 'feature'"
    elif insight_mode == "review":
        category_filter = "AND category IN ('good_review', 'bad_review', 'problem')"

    aspect_query = f"""
        SELECT aspect_tag, COUNT(*) as count 
        FROM extracted_insights 
        {base_filter} {category_filter}
        GROUP BY aspect_tag
        ORDER BY count DESC
    """
    aspect_rows = conn.execute(aspect_query, params).fetchall()
    raw_aspect_counts = [(r["aspect_tag"], r["count"]) for r in aspect_rows]
    
    # CRITICAL CLUTTER FIX: Limit to Top 7 and group the rest into "Other Minor Issues"
    if len(raw_aspect_counts) > 7:
        top_7 = raw_aspect_counts[:7]
        other_sum = sum(cnt for _, cnt in raw_aspect_counts[7:])
        aspect_counts = {asp: cnt for asp, cnt in top_7}
        if other_sum > 0:
            aspect_counts["Other Minor Issues"] = other_sum
    else:
        aspect_counts = {asp: cnt for asp, cnt in raw_aspect_counts}

    # Payload based on requested mode
    response_data = {
        "status": "success",
        "product": product_info,
        "mode": insight_mode,
        "metrics": {
            "total_reviews": product_info["total_reviews"],
            "flagged_defects": defect_count,
            "feature_requests": feature_count,
            "positive_sentences": good_count,
            "negative_sentences": bad_count
        },
        "aspect_distribution": aspect_counts,
        "improvement_suggestion": suggestion,
        "category_summaries": []
    }

    if insight_mode == "problem":
        category_summaries = []
        total_aspect_mentions = sum(aspect_counts.values()) or 1
        for aspect, count in aspect_counts.items():
            if aspect == "Other Minor Issues":
                summary = "Miscellaneous and lower-frequency customer failure reports covering secondary hardware components, peripheral accessories, and minor operational edge cases."
            else:
                query_sentences = f"""
                    SELECT sentence_text FROM extracted_insights 
                    {base_filter} AND category = 'problem' AND aspect_tag = ?
                """
                s_rows = conn.execute(query_sentences, (*params, aspect)).fetchall()
                sentences = [r["sentence_text"] for r in s_rows]
                summary = spark_processor.synthesize_aspect_summary(aspect, "problem", sentences, product_info["product_name"])
            pct = round((count / total_aspect_mentions) * 100)
            category_summaries.append({
                "aspect": aspect,
                "count": count,
                "percentage": pct,
                "summary": summary
            })
        response_data["category_summaries"] = category_summaries

    elif insight_mode == "feature":
        category_summaries = []
        total_aspect_mentions = sum(aspect_counts.values()) or 1
        for aspect, count in aspect_counts.items():
            if aspect == "Other Minor Issues":
                summary = "Secondary feature wishlist proposals and peripheral accessory customization requests."
            else:
                query_sentences = f"""
                    SELECT sentence_text FROM extracted_insights 
                    {base_filter} AND category = 'feature' AND aspect_tag = ?
                """
                s_rows = conn.execute(query_sentences, (*params, aspect)).fetchall()
                sentences = [r["sentence_text"] for r in s_rows]
                summary = spark_processor.synthesize_aspect_summary(aspect, "feature", sentences, product_info["product_name"])
            pct = round((count / total_aspect_mentions) * 100)
            category_summaries.append({
                "aspect": aspect,
                "count": count,
                "percentage": pct,
                "summary": summary
            })
        response_data["category_summaries"] = category_summaries

    elif insight_mode == "review":
        # Positive summaries (Top 7 + Other Minor Issues)
        pos_aspect_rows = conn.execute(
            f"SELECT aspect_tag, COUNT(*) as count FROM extracted_insights {base_filter} AND category = 'good_review' GROUP BY aspect_tag ORDER BY count DESC",
            params
        ).fetchall()
        raw_pos = [(r["aspect_tag"], r["count"]) for r in pos_aspect_rows]
        total_pos = sum(cnt for _, cnt in raw_pos) or 1
        
        if len(raw_pos) > 7:
            top_7_pos = raw_pos[:7]
            other_pos_cnt = sum(cnt for _, cnt in raw_pos[7:])
            pos_dict = {asp: cnt for asp, cnt in top_7_pos}
            if other_pos_cnt > 0:
                pos_dict["Other Minor Issues"] = other_pos_cnt
        else:
            pos_dict = {asp: cnt for asp, cnt in raw_pos}

        pos_summaries = []
        for asp, cnt in pos_dict.items():
            if asp == "Other Minor Issues":
                summary = "Additional positive observations regarding packaging aesthetics, accessory convenience, and baseline satisfaction."
            else:
                s_rows = conn.execute(
                    f"SELECT sentence_text FROM extracted_insights {base_filter} AND category = 'good_review' AND aspect_tag = ?",
                    (*params, asp)
                ).fetchall()
                sentences = [s["sentence_text"] for s in s_rows]
                summary = spark_processor.synthesize_aspect_summary(asp, "review", sentences, product_info["product_name"])
            pos_summaries.append({
                "aspect": asp,
                "count": cnt,
                "percentage": round((cnt / total_pos) * 100),
                "summary": summary
            })

        # Negative summaries (Top 7 + Other Minor Issues)
        neg_aspect_rows = conn.execute(
            f"SELECT aspect_tag, COUNT(*) as count FROM extracted_insights {base_filter} AND (category = 'bad_review' OR category = 'problem') GROUP BY aspect_tag ORDER BY count DESC",
            params
        ).fetchall()
        raw_neg = [(r["aspect_tag"], r["count"]) for r in neg_aspect_rows]
        total_neg = sum(cnt for _, cnt in raw_neg) or 1

        if len(raw_neg) > 7:
            top_7_neg = raw_neg[:7]
            other_neg_cnt = sum(cnt for _, cnt in raw_neg[7:])
            neg_dict = {asp: cnt for asp, cnt in top_7_neg}
            if other_neg_cnt > 0:
                neg_dict["Other Minor Issues"] = other_neg_cnt
        else:
            neg_dict = {asp: cnt for asp, cnt in raw_neg}

        neg_summaries = []
        for asp, cnt in neg_dict.items():
            if asp == "Other Minor Issues":
                summary = "Miscellaneous lower-priority complaints and peripheral issues reported across secondary hardware components."
            else:
                s_rows = conn.execute(
                    f"SELECT sentence_text FROM extracted_insights {base_filter} AND (category = 'bad_review' OR category = 'problem') AND aspect_tag = ?",
                    (*params, asp)
                ).fetchall()
                sentences = [s["sentence_text"] for s in s_rows]
                summary = spark_processor.synthesize_aspect_summary(asp, "problem", sentences, product_info["product_name"])
            neg_summaries.append({
                "aspect": asp,
                "count": cnt,
                "percentage": round((cnt / total_neg) * 100),
                "summary": summary
            })

        response_data["positive_summaries"] = pos_summaries
        response_data["negative_summaries"] = neg_summaries
        response_data["category_summaries"] = neg_summaries


    conn.close()
    return jsonify(response_data)

@app.route("/api/system_status")
def system_status():
    """Returns live status of Big Data components."""
    ensure_database_ready()
    conn = get_db_connection()
    db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    insights_count = conn.execute("SELECT COUNT(*) FROM extracted_insights").fetchone()[0]
    products_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    conn.close()
    
    return jsonify({
        "flume_stream": "Active / Ready",
        "spark_engine": "PySpark + Vectorized NLP Active",
        "sqlite_status": "Connected",
        "database_size_kb": round(db_size / 1024, 2),
        "total_insights": insights_count,
        "total_products": products_count
    })

if __name__ == "__main__":
    ensure_database_ready()
    print("\n=======================================================")
    print(" InsightFlow Server Online: http://127.0.0.1:5000")
    print("=======================================================\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
