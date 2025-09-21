from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3 #DB 파일 연결하고 테이블 생성, insert/select 쿼리 실행, 결과 조회
import os #파일/디렉터리 조작, 환경변수 읽기

DB_PATH = "guestbook.db" #사용자 방명록 DB 파일 생성
SECRET_KEY = os.environ.get("FLASK_SECRET", "change-this-in-prod") #시크릿 키를 환경변수에서 읽기, DB 경로 조합. 없으면 기본값

app = Flask(__name__) #flask 객체 생성
app.config["SECRET_KEY"] = SECRET_KEY

def init_db(): #DB 초기화 함수
    conn = sqlite3.connect(DB_PATH) #DB 연결
    cur = conn.cursor()
    cur.execute(""" #테이블 생성. 있으면 건너뜀
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, #고유 아이디
        name TEXT NOT NULL, #작성자 이름
        message TEXT NOT NULL, #작성한 메시지
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP #작성 시각
    )
    """)
    conn.commit()
    conn.close()

def insert_message(name, message): #메시지 저장 함수
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (name, message) VALUES (?, ?)", (name, message)) #파라미터 바인딩 방식
    conn.commit()
    conn.close()

def get_all_messages(): #전체 메시지 조회 함수
    conn = sqlite3.connect(DB_PATH) #모든 메시지 DB에서 최신순으로 가져옴
    cur = conn.cursor()
    cur.execute("SELECT id, name, message, created_at FROM messages ORDER BY id DESC")
    rows = cur.fetchall() #모든 결과 가져옴
    conn.close()
    return rows

def search_messages(q): #메시지 검색 함수
    conn = sqlite3.connect(DB_PATH) #이름 또는 메시지에 검색어가 포함된 기록 조회
    cur = conn.cursor()
    pattern = f"%{q}%" #부분 일치하는거 다 포함
    cur.execute(
        "SELECT id, name, message, created_at FROM messages WHERE name LIKE ? OR message LIKE ? ORDER BY id DESC",
        (pattern, pattern)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

#라우팅 링크와 함수 연결
@app.route("/", methods=["GET"])
def index():
    #메인 페이지: 검색 폼 + 작성 폼 + 전체 출력
    messages = get_all_messages() #DB에서 전체 메시지 불러옴
    return render_template("index.html", messages=messages, q="", search_mode=False) #일반 목록임을 표시

@app.route("/search", methods=["GET"])
def search():
    #/search : q 파라미터로 검색 결과 출력
    q = request.args.get("q", "").strip() #'q'읽기
    if not q: #빈 검색어일 경우
        flash("검색어를 입력하세요.", "error")
        return redirect(url_for("index")) #메인으로 돌아감
    results = search_messages(q)
    return render_template("index.html", messages=results, q=q, search_mode=True)

@app.route("/write", methods=["POST"])
def write():
    #/write : 이름과 메시지 받아 저장 -> '/'로 리다이렉트
    name = request.form.get("name", "").strip() #post 파라미터 'name'
    message = request.form.get("message", "").strip() #post 파라미터 'message'

    if not name or not message: #둘 다 입력해야 저장
        flash("이름과 메시지를 모두 입력하세요.", "error")
        return redirect(url_for("index"))

    insert_message(name, message) #메시지 저장
    flash("메시지가 저장되었습니다.", "success")
    return redirect(url_for("index")) #메인 페이지로 리다이렉트

if __name__ == "__main__": #애플리케이션 실행
    init_db() #서버 시작시 DB 초기화
    app.run(debug=True, host="127.0.0.1", port=5000)
