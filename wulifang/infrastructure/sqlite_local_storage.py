# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


import contextlib
import sqlite3
from wulifang._util import run_in_main_thread


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional, Iterator
    from wulifang._types import LocalStorageService

# spell-checker: word executescript


@contextlib.contextmanager
def _transaction(con):
    # type: (sqlite3.Connection) -> Iterator[sqlite3.Connection]
    try:
        yield con
        con.commit()
    except:
        con.rollback()
        raise


def _migrate_v1(con):
    # type: (sqlite3.Connection) -> None
    con.executescript(
        """\
BEGIN;
CREATE TABLE "items" (
"key"	TEXT NOT NULL,
"value"	TEXT,
PRIMARY KEY("key")
);
PRAGMA user_version = 1;
COMMIT;
"""
    )


_MIGRATIONS = {
    1: _migrate_v1,
}


class SQLiteLocalStorage:
    def __init__(self, _path=""):
        # type: (Text) -> None
        assert _path, "path is required"
        self._path = _path
        self._conn = None  # type: Optional[sqlite3.Connection]

    def __del__(self):
        if self._conn:
            self._conn.close()

    def _connect(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self._path)
            self._migrate(self._conn)
        return self._conn

    def _txn(self):
        return _transaction(self._connect())

    def _migrate(self, c):
        # type: (sqlite3.Connection) -> None
        (v,) = c.execute("PRAGMA user_version;").fetchone()
        max_version = max(_MIGRATIONS.keys())
        if v > max_version:
            raise RuntimeError(
                "%s: max supported version is %d, got %d" % (self._path, max_version, v)
            )
        while v < max_version:
            next_v = v + 1
            _MIGRATIONS[next_v](c)
            v = next_v

    @run_in_main_thread
    def __delitem__(self, key):
        # type: (Text) -> None

        with self._txn() as c:
            c.execute(
                "DELETE FROM items WHERE key=?;",
                (key),
            )

    @run_in_main_thread
    def __setitem__(self, key, value):
        # type: (Text,Text) -> None
        if not value:
            del self[key]
            return
        with self._txn() as c:
            c.execute(
                "INSERT OR REPLACE INTO items VALUES(?, ?);",
                (key, value),
            )

    @run_in_main_thread
    def __getitem__(self, key):
        # type: (Text) -> Text
        with self._txn() as c:
            row = c.execute(
                "SELECT value FROM items WHERE key = ?;",
                (key,),
            ).fetchone()
            if not row:
                return ""
            return row[0]


def _(v):
    # type: (SQLiteLocalStorage) -> LocalStorageService
    return v
