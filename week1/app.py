from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import bleach

DB_PATH = "guestbook.db"
SECRET_KEY = os.environ.get("FLASK_SECRET", "change-this-in-prod")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def insert_message(name, message):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (name, message) VALUES (?, ?)", (name, message))
    conn.commit()
    conn.close()

def get_all_messages():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, message, created_at FROM messages ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def search_messages(q):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    pattern = f"%{q}%"
    cur.execute(
        "SELECT id, name, message, created_at FROM messages WHERE name LIKE ? OR message LIKE ? ORDER BY id DESC",
        (pattern, pattern)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


@app.route("/", methods=["GET"])
def index():
    """메인 페이지: 검색 폼 + 작성 폼 + 전체 출력"""
    messages = get_all_messages()
    return render_template("index.html", messages=messages, q="", search_mode=False)

@app.route("/search", methods=["GET"])
def search():
    """/search : q 파라미터로 검색 결과 출력"""
    q = request.args.get("q", "").strip()
    if not q:
        flash("검색어를 입력하세요.", "error")
        return redirect(url_for("index"))
    results = search_messages(q)
    return render_template("index.html", messages=results, q=q, search_mode=True)

@app.route("/write", methods=["POST"])
def write():
    """/write : 이름과 메시지 받아 저장 -> '/'로 리다이렉트"""
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not message:
        flash("이름과 메시지를 모두 입력하세요.", "error")
        return redirect(url_for("index"))

    save_name = name
    save_message = message
    insert_message(save_name, save_message)
    flash("메시지가 저장되었습니다.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
