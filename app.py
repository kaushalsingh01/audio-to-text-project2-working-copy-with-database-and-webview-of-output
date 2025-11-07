from flask import Flask, render_template, jsonify, Response, request
import sqlite3
import csv
import io
import os
import transcriber

app = Flask(__name__)

# Start background transcriber
# transcriber.start_transcriber()

DB_FILE = "transcriptions.db"

users = {}

def get_conn():
    return sqlite3.connect(DB_FILE)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"error": "username required"}), 400
    user_id = len(users) + 1
    users[user_id] = username
    return jsonify({"user_id": user_id, "username": username})

@app.route("/start/<username>", methods=["POST"])
def start(username):
    # Find or create user_id
    user_id = next((uid for uid, name in users.items() if name == username), None)
    if not user_id:
        user_id = len(users) + 1
        users[user_id] = username
    if transcriber.start_listening(user_id):
        return jsonify({"status": f"Listening started for {username}", "user_id": user_id})
    return jsonify({"status": "Already listening"}), 400


@app.route("/stop/<username>", methods=["POST"])
def stop(username):
    user_id = next((uid for uid, name in users.items() if name == username), None)
    if not user_id:
        user_id = len(users) + 1
        users[user_id] = username 
    if transcriber.stop_listening(user_id):
        return jsonify({"status": f"Stopped listening for user {user_id}"})
    return  jsonify({"status": "Not active"}), 400

def get_transcripts(user_id=None, limit=None):
    conn = get_conn()
    cursor = conn.cursor()
    query = "SELECT timestamp, text, audio_path FROM transcripts"
    params = []
    if user_id:
        query += " WHERE user_id=?"
        params.append(user_id)
    query += " ORDER BY id DESC"
    if limit:
        query += f" LIMIT {limit}"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [{"timestamp": r[0], "text": r[1], "audio_path": r[2]} for r in rows]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(get_transcripts(limit=20))

@app.route("/teaching_data")
def teaching_data():
    return jsonify(transcriber.get_teaching_messages())

@app.route("/users")
def get_users():
    return jsonify(users)

# 🔹 Download TXT
@app.route("/download/txt")
def download_txt():
    transcripts = get_transcripts()
    output = io.StringIO()
    for t in transcripts:
        output.write(f"{t['timestamp']} - {t['text']}\n")
    return Response(output.getvalue(),
                    mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=transcripts.txt"})

# 🔹 Download CSV
@app.route("/download/csv")
def download_csv():
    transcripts = get_transcripts()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Transcript"])
    for t in transcripts:
        writer.writerow([t['timestamp'], t['text']])
    return Response(output.getvalue(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=transcripts.csv"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)
