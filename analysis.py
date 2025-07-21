import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "asd_detection_db"
}

def fetch_results():
    """Retrieve prediction results from MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT result, confidence, timestamp FROM predictions ORDER BY timestamp DESC")
        data = cursor.fetchall()
        conn.close()
        
        df = pd.DataFrame(data, columns=["Result", "Confidence", "Timestamp"])
        return df
    except Exception as e:
        print("Error fetching data:", e)
        return pd.DataFrame()

def generate_analysis():
    """Generate statistical analysis and visualizations."""
    df = fetch_results()
    
    if df.empty:
        print("No data available for analysis.")
        return

    # Count occurrences of each result
    plt.figure(figsize=(8, 5))
    sns.countplot(x="Result", data=df, palette="coolwarm")
    plt.title("Prediction Results Distribution")
    plt.xlabel("ASD Prediction")
    plt.ylabel("Count")
    plt.savefig("static/uploads/result_distribution.png")
    print("✅ Result distribution saved.")

    # Confidence level analysis
    plt.figure(figsize=(8, 5))
    sns.histplot(df["Confidence"], bins=10, kde=True, color="blue")
    plt.title("Confidence Level Distribution")
    plt.xlabel("Confidence Score")
    plt.ylabel("Frequency")
    plt.savefig("static/uploads/confidence_distribution.png")
    print("✅ Confidence distribution saved.")

    # Print summary statistics
    print("\nSummary Statistics:")
    print(df.describe())

if __name__ == "__main__":
    generate_analysis()
