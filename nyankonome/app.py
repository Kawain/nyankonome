import os
import re
import shutil
import sqlite3
import datetime
import hashlib
from flask import Flask, render_template, url_for, request, redirect, jsonify, escape
import template

"""
にゃんこのめ 下書き作成
2019-04-26 ver. 1.0.0 下書きのみにした
2019-04-16 ver. 0.0.2
2019-04-04 ver. 0.0.1
"""

# データベースファイルのパス
DB_PATH = "./db/nyankonomeonline.db"

# パスワード
PW = "c29277f55fb31aeb8d4026132e53513a1fb755e5d9c13bf21405b72b9570373f"

# インスタンス化
app = Flask(__name__)


def dbaccess():
    """データベースのConnectionとCursorを返す"""

    # もしファイルがなければテーブルを作る
    if not os.path.isfile(DB_PATH):
        create_table()

    # Connection
    conn = sqlite3.connect(DB_PATH)
    # Cursor オブジェクトを作成
    cursor = conn.cursor()

    return conn, cursor


def create_table():
    """もしデータベースファイルがなければ新規にテーブルを作る"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # executeメソッドでSQL文を実行
    cursor.execute("""
CREATE TABLE "draft" (
	"id"	TEXT,
	"editor"	TEXT DEFAULT "",
	"title"	TEXT DEFAULT "",
	"explain"	TEXT DEFAULT "",
	"zip"	INTEGER DEFAULT 0,
	PRIMARY KEY("id")
);
    """)

    conn.commit()
    cursor.close()
    conn.close()


@app.route("/")
def index():
    """トップページ"""

    conn, cursor = dbaccess()

    cursor.execute(
        """SELECT id, editor, title, zip FROM draft ORDER BY id DESC;""")
    # 全件取得は cursor.fetchall()
    # 一つ一つ取り出す場合はfetchone
    lists = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("index.html", lists=lists)


@app.route("/text")
def text():
    """テキスト形式"""

    conn, cursor = dbaccess()

    cursor.execute(
        """SELECT id, editor, title FROM draft ORDER BY id DESC;""")
    lists = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("text.html", lists=lists)


@app.route("/insert", methods=["POST"])
def insert():
    """新規追加"""

    draft_id = request.form["draft_id"]

    # [0-9A-Za-z]以外ならエラー
    if not re.match(r"^[0-9A-Za-z]+$", draft_id):
        return render_template("error.html", message="半角で入力してください")

    conn, cursor = dbaccess()

    # 重複チェック
    cursor.execute(
        """SELECT count(id) FROM draft WHERE id = ?;""", (draft_id,))
    obj = cursor.fetchone()

    # もし重複していれば編集画面にリダイレクト
    if obj[0] > 0:
        cursor.close()
        conn.close()

        return redirect(url_for("form", id=draft_id))

    # 重複がなければ新規追加
    try:
        cursor.execute("""INSERT INTO draft (id) VALUES (?);""", (draft_id,))
        conn.commit()
    except:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    # 編集画面にリダイレクト
    return redirect(url_for("form", id=draft_id))


@app.route("/form/<id>")
def form(id):
    """編集フォーム"""

    return render_template("detail.html", id=id, template=template.template)


@app.route("/html/<id>")
def html(id):
    """HTML表示"""

    conn, cursor = dbaccess()

    cursor.execute("""SELECT explain FROM draft WHERE id = ?;""", (id,))
    obj = cursor.fetchone()

    cursor.close()
    conn.close()

    explain = obj[0]
    # 念のために最後に改行1つ追加
    explain = explain + "<br>"
    # explainの改行を<br>にする win linux mac 用
    explain = explain.replace("\r\n", "<br>")
    explain = explain.replace("\n", "<br>")
    explain = explain.replace("\r", "<br>")
    # templateにexplainを埋め込む
    template2 = template.template.replace(
        '<span v-html="explain2"></span>', explain)

    return escape(template2)


@app.route("/select/<id>")
def select(id):
    """Vue.jsの関係でjsonを返却"""

    conn, cursor = dbaccess()

    cursor.execute("""SELECT * FROM draft WHERE id = ?;""", (id,))
    obj = cursor.fetchone()

    cursor.close()
    conn.close()

    # 辞書に変数を詰め込む
    dic = {
        "id": obj[0],
        "editor": obj[1],
        "title": obj[2],
        "explain": obj[3]
    }

    return jsonify(dic)


@app.route("/update/<id>", methods=["POST"])
def update(id):
    """更新"""

    f = "ng"

    conn, cursor = dbaccess()

    editor = request.form["editor"]
    title = request.form["title"]
    explain = request.form["explain"]

    try:
        cursor.execute("""UPDATE draft SET editor = ?, title = ?, explain = ? WHERE id = ?;""",
                       (editor, title, explain, id))
        conn.commit()
        f = "ok"
    except:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return f


@app.route("/delete", methods=["POST"])
def delete():
    """削除"""

    obj = request.json

    f = "ng"

    pw = hashlib.sha256(obj['pw'].encode()).hexdigest()

    if PW != pw:
        f = "ng"
        return f

    # ファイルをバックアップのためにコピー
    # コピーするファイル名
    copy_db_file = datetime.datetime.today().strftime(f"./db/%Y%m%d_%H%M%S.db")
    shutil.copy(DB_PATH, copy_db_file)

    conn, cursor = dbaccess()

    try:
        for v in obj['check']:
            cursor.execute("""DELETE FROM draft WHERE id=?""", (v,))

        conn.commit()

        # ついでにSQLiteの空き領域開放
        cursor.execute("""VACUUM;""")
        conn.commit()

        f = "ok"
    except:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return f


@app.route("/rest/<id>")
def rest_get(id):
    """REST API GET"""

    conn, cursor = dbaccess()
    cursor.execute("""SELECT * FROM draft WHERE id = ?;""", (id,))
    obj = cursor.fetchone()
    cursor.close()
    conn.close()

    if obj is not None:
        # 辞書に変数を詰め込む
        dic = {
            "id": obj[0],
            "editor": obj[1],
            "title": obj[2],
            "explain": obj[3],
            "zip": obj[4]
        }

        response = jsonify({'results': dic})
        response.status_code = 200
        return response
    else:
        response = jsonify({'results': 'ng'})
        response.status_code = 404
        return response


@app.route("/rest/<id>", methods=['PUT'])
def rest_put(id):
    """REST API PUT"""

    conn, cursor = dbaccess()

    f = "ng"
    try:
        cursor.execute("""UPDATE draft SET zip = 1 WHERE id = ?;""", (id,))
        conn.commit()
        f = "ok"
    except:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    if f:
        response = jsonify({'results': 'ok'})
        response.status_code = 200
        return response
    else:
        response = jsonify({'results': 'ng'})
        response.status_code = 500
        response = response


if __name__ == '__main__':
    app.run(port="8989", debug=False, threaded=True)
