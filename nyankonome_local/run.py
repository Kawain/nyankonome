import os
import shutil
import re
import csv
import requests
import json
import datetime
import template
import img_resize

# 画像を置くフォルダ
WORK_FOLDER = "./images"

# 完成したZIPファイルの場所
ZIP_PATH = "./zip/"

# サーバーの resr URL
URL = "https://nyankonome.liveinhope.biz/rest/"
# URL = "http://127.0.0.1:8989/rest/"


def check_folder():
    """WORK_FOLDERの中身をチェック"""

    # 1回目
    files = os.listdir(WORK_FOLDER)
    if len(files) == 0:
        return "中身がありません。ID名のフォルダに画像を入れて置いてください。"

    # 空のディレクトリがあれば削除
    for v in files:
        try:
            os.rmdir(f"{WORK_FOLDER}/{v}")
        except:
            pass

    # 2回目
    files = os.listdir(f"{WORK_FOLDER}")
    if len(files) == 0:
        return "空のフォルダでした。削除しました。"

    # 削除リスト
    del_files = []

    # 第一階層の削除リスト追加
    # コンパイル
    r = re.compile(r"^[0-9A-Za-z]+$")
    for v in files:
        if not r.match(v):
            # [0-9A-Za-z]以外のフォルダ名
            del_files.append(f"{WORK_FOLDER}/{v}")
        elif not os.path.isdir(f"{WORK_FOLDER}/{v}"):
            # ファイルであれば
            del_files.append(f"{WORK_FOLDER}/{v}")

    # 削除
    for v in del_files:
        if os.path.isdir(v):
            shutil.rmtree(v)
        else:
            os.remove(v)

    # 3回目
    files = os.listdir(WORK_FOLDER)
    if len(files) == 0:
        return "関係ないファイルでした。削除しました。"

    # 削除リスト
    del_files = []
    # 第一階層のフォルダ内をチェック
    for v1 in files:
        v2 = os.listdir(f"{WORK_FOLDER}/{v1}")
        for v3 in v2:
            # .jpg以外のファイルは削除リストに追加(ディレクトリも含む)
            if not v3.endswith(".jpg"):
                del_files.append(f"{WORK_FOLDER}/{v1}/{v3}")

    # 削除
    for v in del_files:
        if os.path.isdir(v):
            shutil.rmtree(v)
        else:
            os.remove(v)

    # 空のディレクトリがあれば削除
    for v in files:
        try:
            os.rmdir(f"{WORK_FOLDER}/{v}")
        except:
            pass

    # 4回目
    files = os.listdir(f"{WORK_FOLDER}")
    if len(files) == 0:
        return "関係ないファイルでした。削除しました。"

    return files


def server_id_check(folder_id):
    """サーバーにあるIDと照らし合わせて、サーバーにないIDフォルダは削除"""

    for v in folder_id:
        url = f"{URL}{v}"
        r = requests.get(url)
        j = r.json()
        if j['results'] == 'ng':
            shutil.rmtree(f"{WORK_FOLDER}/{v}")

    # 5回目
    files = os.listdir(f"{WORK_FOLDER}")
    if len(files) == 0:
        return "下書きにないIDフォルダでしたので削除しました。"

    return files


def server_update_zip(folder_id):
    """サーバーにあるIDのzipカラムを更新"""
    for v in folder_id:
        url = f"{URL}{v}"
        r = requests.put(url)
        j = r.json()
        if j['results'] == 'ng':
            shutil.rmtree(f"{WORK_FOLDER}/{v}")
            print(f"{v}の更新に失敗したのでフォルダを削除しました。")
        else:
            print(f"{v}の更新成功")


def make_image():
    """フォルダ名＿ファイル名の画像作成"""

    g = os.walk(WORK_FOLDER)

    folders = g.__next__()[1]

    i = 0
    while True:
        try:
            lst = g.__next__()[2]
            for v in lst:
                # ファイルを移動してリネーム
                old_name = f"{WORK_FOLDER}/{folders[i]}/{v}"
                new_name = f"{WORK_FOLDER}/{folders[i]}_{v}"
                # ファイルを移動してリネーム
                a = shutil.move(old_name, new_name)
                print(a, "ファイルを移動してリネームしました")

        except:
            break
        i += 1

    # フォルダ(中にファイルがあっても)削除
    for v in folders:
        shutil.rmtree(f"{WORK_FOLDER}/{v}")


def get_contents(id):
    """サーバーにある下書きを取得"""
    url = f"{URL}{id}"
    r = requests.get(url)
    return r.json()


def returnColumns():
    """列の定義"""

    columns = []

    # columns.append(["カテゴリ", 2084051973])
    # columns.append(["タイトル", ""])
    # columns.append(["説明", ""])
    # columns.append(["開始価格", 600])
    # columns.append(["個数", 1])
    # columns.append(["開催期間", 7])
    # columns.append(["終了時間", 8])
    # columns.append(["画像1", ""])
    # columns.append(["画像2", ""])
    # columns.append(["画像3", ""])
    # columns.append(["画像4", ""])
    # columns.append(["画像5", ""])
    # columns.append(["画像6", ""])
    # columns.append(["画像7", ""])
    # columns.append(["画像8", ""])
    # columns.append(["画像9", ""])
    # columns.append(["画像10", ""])
    # columns.append(["商品発送元の都道府県", "北海道"])
    # columns.append(["送料負担", "落札者"])
    # columns.append(["代金支払い", "先払い"])
    # columns.append(["Yahoo!かんたん決済", "はい"])
    # columns.append(["かんたん取引", "はい"])
    # columns.append(["商品代引", "いいえ"])
    # columns.append(["商品の状態", "目立った傷や汚れなし"])
    # columns.append(["返品の可否", "返品不可"])
    # columns.append(["入札者評価制限", "いいえ"])
    # columns.append(["悪い評価の割合での制限", "いいえ"])
    # columns.append(["入札者認証制限", "いいえ"])
    # columns.append(["自動延長", "はい"])
    # columns.append(["早期終了", "はい"])
    # columns.append(["値下げ交渉", "いいえ"])
    # columns.append(["自動再出品", 3])
    # columns.append(["自動値下げ", "いいえ"])
    # columns.append(["自動値下げ価格変更率", ""])
    # columns.append(["太字テキスト", "いいえ"])
    # columns.append(["背景色", "いいえ"])
    # columns.append(["贈答品アイコン", "いいえ"])
    # columns.append(["送料固定", "はい"])
    # columns.append(["ネコポス", "いいえ"])
    # columns.append(["ネコ宅急便コンパクト", "いいえ"])
    # columns.append(["ネコ宅急便", "いいえ"])
    # columns.append(["ゆうパケット", "いいえ"])
    # columns.append(["ゆうパック", "いいえ"])
    # columns.append(["配送方法1", "クリックポスト"])
    # columns.append(["配送方法1全国一律価格", 185])
    # columns.append(["受け取り後決済サービス", "いいえ"])
    # columns.append(["海外発送", "いいえ"])
    # columns.append(["アフィリエイト", "いいえ"])
    # columns.append(["出品者情報開示前チェック", "いいえ"])

    columns.append(["カテゴリ", 2084052388])
    columns.append(["タイトル", ""])
    columns.append(["説明", ""])
    columns.append(["開始価格", 600])
    columns.append(["即決価格", ""])
    columns.append(["個数", 1])
    columns.append(["開催期間", 7])
    columns.append(["終了時間", 20])
    columns.append(["JANコード", ""])
    columns.append(["画像1", ""])
    columns.append(["画像1コメント", ""])
    columns.append(["画像2", ""])
    columns.append(["画像2コメント", ""])
    columns.append(["画像3", ""])
    columns.append(["画像3コメント", ""])
    columns.append(["画像4", ""])
    columns.append(["画像4コメント", ""])
    columns.append(["画像5", ""])
    columns.append(["画像5コメント", ""])
    columns.append(["画像6", ""])
    columns.append(["画像6コメント", ""])
    columns.append(["画像7", ""])
    columns.append(["画像7コメント", ""])
    columns.append(["画像8", ""])
    columns.append(["画像8コメント", ""])
    columns.append(["画像9", ""])
    columns.append(["画像9コメント", ""])
    columns.append(["画像10", ""])
    columns.append(["画像10コメント", ""])
    columns.append(["商品発送元の都道府県", "北海道"])
    columns.append(["商品発送元の市区町村", ""])
    columns.append(["送料負担", "落札者"])
    columns.append(["代金支払い", "先払い"])
    columns.append(["Yahoo!かんたん決済", "はい"])
    columns.append(["かんたん取引", "はい"])
    columns.append(["商品代引", "いいえ"])
    columns.append(["商品の状態", "やや傷や汚れあり"])
    columns.append(["商品の状態備考", ""])
    columns.append(["返品の可否", "返品不可"])
    columns.append(["返品の可否備考", ""])
    columns.append(["入札者評価制限", "いいえ"])
    columns.append(["悪い評価の割合での制限", "いいえ"])
    columns.append(["入札者認証制限", "いいえ"])
    columns.append(["自動延長", "はい"])
    columns.append(["早期終了", "はい"])
    columns.append(["値下げ交渉", "いいえ"])
    columns.append(["自動再出品", 3])
    columns.append(["自動値下げ", "いいえ"])
    columns.append(["自動値下げ価格変更率", ""])
    columns.append(["最低落札価格", ""])
    columns.append(["注目のオークション", ""])
    columns.append(["おすすめコレクション", ""])
    columns.append(["太字テキスト", "いいえ"])
    columns.append(["背景色", "いいえ"])
    columns.append(["目立ちアイコン", ""])
    columns.append(["贈答品アイコン", "いいえ"])
    columns.append(["送料固定", "はい"])
    columns.append(["荷物の大きさ", ""])
    columns.append(["荷物の重量", ""])
    columns.append(["ネコポス", "いいえ"])
    columns.append(["ネコ宅急便コンパクト", "いいえ"])
    columns.append(["ネコ宅急便", "いいえ"])
    columns.append(["ゆうパケット", "いいえ"])
    columns.append(["ゆうパック", "いいえ"])
    columns.append(["発送までの日数", ""])
    columns.append(["配送方法1", "クリックポスト"])
    columns.append(["配送方法1全国一律価格", 185])
    columns.append(["北海道料金1", ""])
    columns.append(["沖縄料金1", ""])
    columns.append(["離島料金1", ""])
    columns.append(["配送方法2", ""])
    columns.append(["配送方法2全国一律価格", ""])
    columns.append(["北海道料金2", ""])
    columns.append(["沖縄料金2", ""])
    columns.append(["離島料金2", ""])
    columns.append(["配送方法3", ""])
    columns.append(["配送方法3全国一律価格", ""])
    columns.append(["北海道料金3", ""])
    columns.append(["沖縄料金3", ""])
    columns.append(["離島料金3", ""])
    columns.append(["配送方法4", ""])
    columns.append(["配送方法4全国一律価格", ""])
    columns.append(["北海道料金4", ""])
    columns.append(["沖縄料金4", ""])
    columns.append(["離島料金4", ""])
    columns.append(["配送方法5", ""])
    columns.append(["配送方法5全国一律価格", ""])
    columns.append(["北海道料金5", ""])
    columns.append(["沖縄料金5", ""])
    columns.append(["離島料金5", ""])
    columns.append(["配送方法6", ""])
    columns.append(["配送方法6全国一律価格", ""])
    columns.append(["北海道料金6", ""])
    columns.append(["沖縄料金6", ""])
    columns.append(["離島料金6", ""])
    columns.append(["配送方法7", ""])
    columns.append(["配送方法7全国一律価格", ""])
    columns.append(["北海道料金7", ""])
    columns.append(["沖縄料金7", ""])
    columns.append(["離島料金7", ""])
    columns.append(["配送方法8", ""])
    columns.append(["配送方法8全国一律価格", ""])
    columns.append(["北海道料金8", ""])
    columns.append(["沖縄料金8", ""])
    columns.append(["離島料金8", ""])
    columns.append(["配送方法9", ""])
    columns.append(["配送方法9全国一律価格", ""])
    columns.append(["北海道料金9", ""])
    columns.append(["沖縄料金9", ""])
    columns.append(["離島料金9", ""])
    columns.append(["配送方法10", ""])
    columns.append(["配送方法10全国一律価格", ""])
    columns.append(["北海道料金10", ""])
    columns.append(["沖縄料金10", ""])
    columns.append(["離島料金10", ""])
    columns.append(["受け取り後決済サービス", "いいえ"])
    columns.append(["海外発送", "いいえ"])
    columns.append(["アフィリエイト", "いいえ"])
    columns.append(["アフィリエイト報酬率", ""])
    columns.append(["出品者情報開示前チェック", "いいえ"])

    return columns


def csv_column(csv_file):
    """列作成"""

    columns = returnColumns()
    _columns = []
    for v in columns:
        _columns.append(v[0])

    with open(csv_file, "a", newline="", encoding='shift_jis') as f:
        # 「delimiter」に区切り文字、「quotechar」に囲い文字を指定します
        # quoting=csv.QUOTE_MINIMALを指定 必要な箇所だけに囲い文字（"）が付与
        writer = csv.writer(f, delimiter=",", quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)

        # writerowに行列を指定することで1行分を出力
        writer.writerow(_columns)


def get_images(id):
    """画像抽出"""

    lists = []
    files = os.listdir(WORK_FOLDER)
    for v in files:
        if v.startswith(id + "_"):
            lists.append(v)

    return lists


def csv_row(csv_file, id, title, explain):
    """行追加"""

    # 念のために最後に改行1つ追加
    explain = explain + "<br>"
    # explainの改行を<br>にする win linux mac 用
    explain = explain.replace("\r\n", "<br>")
    explain = explain.replace("\n", "<br>")
    explain = explain.replace("\r", "<br>")
    # templateにexplainを埋め込む
    template2 = template.template.replace(
        '<span v-html="explain2"></span>', explain)
    # template2の改行削除
    template2 = template2.replace("\r\n", "")
    template2 = template2.replace("\n", "")
    template2 = template2.replace("\r", "")

    # 画像イテレータ作成
    images = iter(get_images(id))

    # 正規表現コンパイル
    imgpat = re.compile(r"^画像\d+$")

    with open(csv_file, "a", newline="", encoding='shift_jis') as f:
        # 「delimiter」に区切り文字、「quotechar」に囲い文字を指定します
        writer = csv.writer(f, delimiter=",", quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)

        row = returnColumns()
        _row = []
        for v in row:
            if v[0] == "タイトル":
                _row.append(title)
            elif v[0] == "説明":
                _row.append(template2)
            elif imgpat.match(v[0]):
                try:
                    _row.append(images.__next__())
                except:
                    _row.append("")
            else:
                _row.append(v[1])

        writer.writerow(_row)


def main():
    print("""
「にゃんこのめ用オークタウンZIPファイル作成システム」
　※インターネットにつながっている必要があります

    """)
    print("【開始】")

    flag = True

    if not os.path.exists(WORK_FOLDER) or not os.path.exists(ZIP_PATH):
        print(WORK_FOLDER, ZIP_PATH, "所定のフォルダが存在していません")
        flag = False

    if flag:
        folder_id = check_folder()
        if type(folder_id) is not list:
            print(folder_id)
            flag = False

    if flag:
        folder_id = server_id_check(folder_id)

        if type(folder_id) is not list:
            print(folder_id)
            flag = False

    # 画像リサイズ追加
    if flag:
        img_resize.main(WORK_FOLDER)

    if flag:
        print()
        server_update_zip(folder_id)
        print()
        make_image()
        print()

    if flag:
        # ファイル名に使う文字列
        file_name = datetime.datetime.today().strftime(f"%Y%m%d_%H%M%S")

        # csvファイル名
        csv_file = f"{WORK_FOLDER}/{file_name}.csv"

        # csvの列だけ作成
        csv_column(csv_file)

        # ループしてcsvの行作成
        for v in folder_id:
            j = get_contents(v)
            id = j['results']['id']
            title = j['results']['title']
            explain = j['results']['explain']
            print(id)
            csv_row(csv_file, id, title, explain)

        # zipにする
        shutil.make_archive(ZIP_PATH + file_name, 'zip', WORK_FOLDER)

        # WORK_FOLDERの残りを削除
        for root, dirs, files in os.walk(WORK_FOLDER, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        print()
        print(ZIP_PATH + file_name + '.zip', "ファイルを作成しました")

    print("【終了】")


if __name__ == "__main__":
    main()
