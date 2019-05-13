import os
# pip install pillow
from PIL import Image


def main(WORK_FOLDER):
    """画像が大きいのでリサイズ"""

    g = os.walk(WORK_FOLDER)

    jpgs = []
    i = 0
    for v in g:
        if i > 0:
            # 気持ちが悪いのでバックスラッシュを置換
            rep = v[0].replace("\\", "/")
            for jpg in v[2]:
                if jpg.endswith(".jpg"):
                    jpgs.append(f"{rep}/{jpg}")

        i += 1

    for jpg in jpgs:
        print(f"{jpg} リサイズ中…")
        img = Image.open(jpg)
        img.thumbnail((1000, 1000), Image.ANTIALIAS)
        img.save(jpg, 'JPEG', quality=100, optimize=True)


if __name__ == "__main__":
    main("./images")
