
import time
import os

FILE_PATH = 'anime_data.json'


def watch_file(path):
    print(f"مراقبة الملف: {path}")
    last_mtime = None
    while True:
        try:
            mtime = os.path.getmtime(path)
            if last_mtime is None:
                last_mtime = mtime
            elif mtime != last_mtime:
                print(f"تم تعديل الملف: {path}")
                last_mtime = mtime
        except FileNotFoundError:
            print(f"الملف غير موجود: {path}")
        time.sleep(1)


if __name__ == "__main__":
    watch_file(FILE_PATH) 