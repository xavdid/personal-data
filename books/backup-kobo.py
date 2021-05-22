from datetime import date
from os import environ
from pathlib import Path
from shutil import copy

from utils import DB_FILENAME, find_kobo_db


def main():
    db = find_kobo_db()
    if not environ.get("DROPBOX"):
        raise ValueError("Define $DROPBOX in env")

    backup_folder = Path(environ["DROPBOX"], "Apps", "Kobo")

    destination = Path(backup_folder, f"{date.today().isoformat()}-{DB_FILENAME}")

    copy(db, destination)
    print("Done! Created", destination)


if __name__ == "__main__":
    main()
