import sys
from pathlib import Path

DB_FILENAME = "KoboReader.sqlite"

POSSIBLE_PATHS = (
    Path("/Volumes", "KOBOeReader", ".kobo", DB_FILENAME),
    Path(Path.home(), "Desktop", DB_FILENAME),
)


def find_kobo_db():
    # checks a couple of default places for the file, or asks or a path
    # default is the connected device

    for p in POSSIBLE_PATHS:
        if p.exists():
            return p

    if len(sys.argv) > 1 and "sqlite" in sys.argv[1]:
        return sys.argv[1]

    raise ValueError(
        "Unable to locate sqlite backup. Re-run the script and provide a path as the first argument"
    )
