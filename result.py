import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "asd_detection_db"
}

def get_results():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT filename, result, confidence, timestamp FROM predictions ORDER BY timestamp DESC")
        data = cursor.fetchall()
        conn.close()

        results = [
            {"filename": row[0], "prediction": row[1], "confidence": row[2], "timestamp": row[3]}
            for row in data
        ]

        return results
    except Exception as e:
        print("Error fetching results:", e)
        return []
