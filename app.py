from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, session, url_for
import MySQLdb
from datetime import timedelta, datetime
import secrets


def connect():
    """phpMyAdminで作成したMySQLデータベースに接続"""
    try:
        con = MySQLdb.connect(
            host="localhost",
            user="root",
            passwd="asd", 
            db="sample",   
            use_unicode=True,
            charset="utf8mb4"
        )
        return con
    except MySQLdb.Error as e:
        print(f"データベース接続エラー: {e}")
        return None

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)  # セッション用の秘密鍵
app.permanent_session_lifetime = timedelta(minutes=60)

@app.route("/make", methods=["GET", "POST"])
def make():
    if request.method == "GET":
        return render_template("make.html")

    elif request.method == "POST":
        email = request.form["email"]
        passwd = request.form["passwd"]
        name = request.form["name"]
        tel = request.form["tel"]

        # パスワードをハッシュ化
        hashpass = generate_password_hash(passwd)
        if "confirm" in request.form:  # 登録確認のページから戻ってきた場合
            # ユーザー情報をデータベースに登録
            con = connect()
            if not con:
                return render_template("make.html", msg="データベース接続に失敗しました")

            try:
                cur = con.cursor()

                # メールアドレスの重複チェック
                cur.execute("SELECT * FROM users WHERE email = %(email)s", {"email": email})
                data = cur.fetchone()
                if data:
                    return render_template("make.html", msg="既に存在するメールアドレスです")

                # 新規ユーザー登録
                cur.execute(""" 
                    INSERT INTO users (email, passwd, tel, name)
                    VALUES (%(email)s, %(hashpass)s, %(tel)s, %(name)s)
                """, {"email": email, "hashpass": hashpass, "tel": tel, "name": name})
                con.commit()

                # 登録後にログインページにリダイレクト
                return redirect(url_for("login"))

            except MySQLdb.Error as e:
                print(f"SQLエラー: {e}")
                return render_template("make.html", msg="登録に失敗しました")
            finally:
                con.close()

        else:
            # 確認画面に遷移
            return render_template("confirm.html", email=email, name=name, tel=tel, passwd=passwd)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")  
        passwd = request.form.get("passwd")

        if not email or not passwd:
            return render_template("login.html", msg="メールアドレスとパスワードを入力してください")

        con = connect()
        if not con:
            return render_template("login.html", msg="データベース接続に失敗しました")

        try:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

            if user is None:
                return render_template("login.html", msg="存在しないアカウントです")

            # デバッグ用ログ
            if check_password_hash(user[2], passwd):
                print("Password match: True")
            else:
                print("Password match: False")

            # パスワードの照合
            if check_password_hash(user[2], passwd):  # user[2] はハッシュ化されたパスワード
                # 認証成功
                session['user_id'] = user[0]  # ユーザーIDをセッションに保存
                session['user_name'] = user[4]  # ユーザー名をセッションに保存（user[4]はnameのカラム）
                session['email'] = email  # emailもセッションに保存
                session['is_admin'] = user[5] 
                print(session)

                # 最終ログイン時刻を更新
                cur.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user[0],))
                con.commit()

                print(session)

                if session['is_admin']:
                    return redirect(url_for("admin_dashboard"))

                return redirect(url_for("home"))  # ログイン後のページへ
            else:
                return render_template("login.html", msg="パスワードが間違っています")
        except MySQLdb.Error as e:
            print(f"SQLエラー: {e}")
            return render_template("login.html", msg="ログインに失敗しました")
        finally:
            con.close()
    return render_template("login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    """管理者用ダッシュボード"""
    if "email" not in session or not session.get("is_admin", False):
        return redirect(url_for("login"))

    con = connect()
    if not con:
        return render_template("error.html", msg="データベース接続に失敗しました")

    try:
        cur = con.cursor()
        # 全ユーザー情報を取得
        cur.execute("SELECT id, name, email, tel, admin, last_login FROM users")
        users = cur.fetchall()

        # 各ユーザーごとの勉強時間の合計を取得
        cur.execute("""
            SELECT u.id, u.name, SUM(r.study_time) AS total_study_time
            FROM users u
            LEFT JOIN study_records r ON u.email = r.user_email
            GROUP BY u.id, u.name
        """)
        study_times = cur.fetchall()

        # 全ユーザーの学習記録を取得
        cur.execute("""
            SELECT u.name, r.category, r.study_date, r.study_time 
            FROM study_records r
            JOIN users u ON r.user_email = u.email
            ORDER BY r.study_date DESC
        """)
        study_records = cur.fetchall()

        con.close()

        return render_template(
            "admin_dashboard.html",
            users=users,
            study_times=study_times
        )
    except MySQLdb.Error as e:
        print(f"SQLエラー: {e}")
        return render_template("error.html", msg="データ取得に失敗しました")

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    print(f"受け取ったユーザーID: {user_id}")  

    """特定のユーザーを削除"""
    if "email" not in session or not session.get("is_admin", False):
        return redirect(url_for("login"))

    con = connect()
    if not con:
        return render_template("error.html", msg="データベース接続に失敗しました")

    try:
        cur = con.cursor()

        # ユーザーの存在確認
        cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        print(f"削除するユーザー: {user}")

        if not user:
            return render_template("error.html", msg="指定されたユーザーは存在しません")
        
        # 自分自身の削除を防止
        if session['user_id'] == user_id:
            return render_template("error.html", msg="自分自身を削除することはできません")

        # ユーザーを削除（ON DELETE CASCADEで関連データも削除）
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        con.commit()

        

        return redirect(url_for("admin_dashboard", msg="ユーザーを削除しました"))
    except MySQLdb.Error as e:
        print(f"SQLエラー: {e}")
        return render_template("error.html", msg="ユーザー削除に失敗しました")
    finally:
        con.close()


@app.route("/home")
def home():
    print(f"セッション内容: {session}")  # セッションの中身を確認
    if "email" not in session:
        return redirect(url_for("login"))

    user_email = session["email"]
    user_name = session["user_name"]
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # 月曜日を基準とした週の始まり
    start_of_month = today.replace(day=1)  # 今月の1日

    con = connect()
    if not con:
        return render_template("error.html", msg="データベース接続に失敗しました")

    try:
        cur = con.cursor()

        # 今日の勉強時間
        cur.execute(""" 
            SELECT SUM(study_time) 
            FROM study_records 
            WHERE user_email = %s AND study_date = %s
        """, (user_email, today))
        daily_time = cur.fetchone()[0] or 0

        # 今週の勉強時間
        cur.execute(""" 
            SELECT SUM(study_time) 
            FROM study_records 
            WHERE user_email = %s AND study_date BETWEEN %s AND %s
        """, (user_email, start_of_week, today))
        weekly_time = cur.fetchone()[0] or 0

        # 今月の勉強時間
        cur.execute(""" 
            SELECT SUM(study_time) 
            FROM study_records 
            WHERE user_email = %s AND study_date BETWEEN %s AND %s
        """, (user_email, start_of_month, today))
        monthly_time = cur.fetchone()[0] or 0

        con.close()

        return render_template(
            "home.html",
            name=session["user_name"],  # セッション情報を利用
            email=session["email"],
            daily_time=daily_time,
            weekly_time=weekly_time,
            monthly_time=monthly_time
        )
    except MySQLdb.Error as e:
        print(f"SQLエラー: {e}")
        con.close()
        return render_template("error.html", msg="データ取得に失敗しました")


@app.route("/add_study_record", methods=["GET", "POST"])
def add_study_record():
    if "email" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        category = request.form["category"]
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        study_date = request.form["study_date"]
        email = session["email"]

        # ここで確認
        print(f"Start Time: {start_time}")
        print(f"End Time: {end_time}")

        # start_time と end_time を datetime 型に変換
        start_time = datetime.strptime(start_time.replace('T', ' '), '%Y-%m-%d %H:%M')
        end_time = datetime.strptime(end_time.replace('T', ' '), '%Y-%m-%d %H:%M')
        

        # 変換後の確認
        print(f"Parsed Start Time: {start_time}")
        print(f"Parsed End Time: {end_time}")

        # 学習時間を計算 (秒単位) -> 分単位に変換
        # study_time = (end_time - start_time).seconds // 60
        # study_time = int(study_time)  # 小数点以下を切り捨て
        study_time_minutes = (end_time - start_time).seconds // 60

        # 時間と分に変換
        hours = study_time_minutes // 60  # 時間
        minutes = study_time_minutes % 60  # 残りの分

        # デバッグ用ログ
        print(f"Study Time: {hours} hours {minutes} minutes")

        # データベースに保存
        con = connect()
        cur = con.cursor()
        cur.execute(""" 
            INSERT INTO study_records (user_email, category, start_time, end_time, study_date, study_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (email, category, start_time, end_time, study_date, study_time_minutes))
        con.commit()
        con.close()
        
        return redirect(url_for("view_study_records"))
    
    return render_template("add_study_record.html")

@app.route("/view_study_records", methods=["GET"])
def view_study_records():
    if "email" not in session:
        return redirect(url_for("login"))
    
    email = session["email"]
    
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT category, start_time, end_time, study_date, study_time FROM study_records WHERE user_email = %s", (email,))
    study_records = cur.fetchall()
    con.close()
    
    return render_template("view_study_records.html", study_records=study_records)

@app.route("/weekly_study_graph")
def weekly_study_graph():
    if "email" not in session:
        return redirect(url_for("login"))

    email = session["email"]
    week_offset = int(request.args.get("week_offset", 0))  # クエリパラメータから週のオフセットを取得
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    con = connect()
    if not con:
        return render_template("error.html", msg="データベース接続に失敗しました")

    try:
        cur = con.cursor()
        # 指定された週の勉強時間データを取得
        cur.execute("""
            SELECT study_date, SUM(study_time) 
            FROM study_records 
            WHERE user_email = %s AND study_date BETWEEN %s AND %s
            GROUP BY study_date
        """, (email, start_of_week, end_of_week))
        
        # データ取得
        records = cur.fetchall()
        con.close()

        # データを整形
        days_of_week = [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        study_times = [0] * 7  # 初期値0
        for record in records:
            day_index = (record[0] - start_of_week).days  # 日付から曜日インデックスを計算
            study_times[day_index] = record[1]  # 勉強時間を格納

        # テンプレートにデータを渡す
        return render_template("weekly_study_graph.html", study_times=study_times, days=days_of_week)

    except MySQLdb.Error as e:
        print(f"SQLエラー: {e}")
        return render_template("error.html", msg="データ取得に失敗しました")


@app.route("/logout")
def logout():
    """セッションをクリアしてログインページにリダイレクト"""
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
