# InsightFlow: E-Commerce Product Intelligence Engine

InsightFlow is a full-stack big data application engineered to transform raw, large-scale customer reviews into actionable root-cause intelligence. Moving beyond traditional positive/negative sentiment percentages, the system utilizes Natural Language Processing (NLP) to extract exact hardware defects, synthesize engineering recommendations, and identify future product requirements via a human-readable SaaS dashboard.

## 🚀 Key Analytical Modes
*   **🚨 Problem Mode (Critical Defects):** Scans for defect-heavy language to isolate severe manufacturing flaws, return drivers, and safety hazards, alerting QA teams before millions are lost.
*   **💬 Review Mode (Balanced Feedback):** Separates product strengths from weaknesses and automatically synthesizes a concrete "Actionable Engineering Recommendation."
*   **💡 Feature Mode (Customer Wishlist):** Utilizes modal pattern matching to extract unfulfilled customer expectations, providing the R&D team with a direct roadmap for the next product iteration.

## 🛠️ Technical Architecture & Stack
*   **Data Ingestion & NLP Engine:** Python, Apache PySpark
*   **Backend Microservice:** Flask, Werkzeug
*   **Centralized Storage:** SQLite
*   **Machine Learning / NLP:** VADER Sentiment, Regex Pattern Matching, Scikit-Learn
*   **Frontend UI:** HTML5, Tailwind CSS, JavaScript (AJAX), Chart.js

## ⚙️ Enterprise Scalability Features
*   **Dynamic Category Summarization:** Instead of rendering thousands of raw quotes that would crash a browser, the system aggregates identical aspect tags and uses extractive summarization to present one clean, high-level summary per category.
*   **Top-N Data Filtering:** Automatically groups minor edge cases into an "Other Minor Issues" bucket, ensuring charts remain clean, readable, and highly focused on the most critical metrics regardless of dataset size (up to 500MB+).
*   **Asynchronous Processing:** Handles massive CSV uploads via an AJAX-powered Flask backend with live 0-100% progress tracking.

## 💻 Installation & Usage

### 1. Clone the Repository

Bash
* git clone [https://github.com/vivikash239-star/InsightFlow.git](https://github.com/vivikash239-star/InsightFlow.git)
* cd InsightFlow

Installation & Usage
1. Clone the Repository

Bash
* git clone [https://github.com/vivikash239-star/InsightFlow.git](https://github.com/vivikash239-star/InsightFlow.git)
* cd InsightFlow

2. Run the Application
The project includes an automated launcher that installs missing dependencies, generates a seed dataset (if no data is present), processes the NLP pipeline, and starts the server.

Bash
* python app.py

3. Access the Dashboard
Open your web browser and navigate to: http://127.0.0.1:5000

Using Custom Datasets
InsightFlow comes with a built-in sample data generator (generate_data.py). To analyze your own data, simply open the web dashboard and use the Upload Dataset panel to upload any CSV file. The system will automatically process the new file, update the database, and render the new insights without requiring a manual restart.