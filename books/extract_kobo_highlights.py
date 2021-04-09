import sqlite3
from pathlib import Path
import json
import sys

HIGHLIGHTS_QUERY = """
SELECT DISTINCT bookmarkid,
                text,
                content.booktitle,
                annotation,
                bookmark.DateCreated
FROM            Bookmark
LEFT OUTER JOIN content
ON              Bookmark.volumeid = content.bookid
WHERE           text NOT null
ORDER BY        Bookmark.datecreated
"""

UNICODE_REPLACEMENTS = {
    "\u2014": "-",
    "\u201c": '"',
    "\u201d": '"',
    "\u00bd": "1/2",
    "\u2019": "'",
    "\u00a0": " ",
    "\u2018": "'",
    "\u2026": "...",
    "\u2013": "-",
}

POSSIBLE_PATHS = (
    Path("/Volumes", "KOBOeReader", ".kobo", "KoboReader.sqlite"),
    Path(Path.home(), "Desktop", "KoboReader.sqlite"),
)


def replace_unicode(s):
    for u, r in UNICODE_REPLACEMENTS.items():
        if u in s:
            s = s.replace(u, r)
    return s


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


def main():
    """
    Dumps a mostly raw version of my Kobo highlights. It:
        * joins text that might be split over multiple lines
        * removes unicode
        * outputs a structure that Zapier expects (https://zapier.com/app/editor/106024564).
    """
    conn = sqlite3.connect(find_kobo_db())
    cur = conn.cursor()
    cur.execute(HIGHLIGHTS_QUERY)

    highlights = []

    for bookmark in cur.fetchall():
        uuid, text, book_title, comment, date_created, = bookmark

        normalized_text = replace_unicode(
            (" ".join([line.strip() for line in text.split("\n") if line]))
        )

        # will throw if there are any unhandled unicode characters left
        assert all([ord(c) < 128 for c in normalized_text])

        highlights.append(
            dict(
                highlight_uuid=uuid,  # zapier dedups on this
                text=normalized_text,
                book_title=book_title,
                comment=comment,
                utc_timestamp=date_created + "Z",
            )
        )

    # probably don't need this at the end of the script, but doesn't hurt
    conn.close()

    Path(
        Path.home(), "projects", "personal-data", "books", "highlights.json"
    ).write_text(json.dumps({"highlights": highlights}, indent=2) + "\n")


if __name__ == "__main__":
    main()
