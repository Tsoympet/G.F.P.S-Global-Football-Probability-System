import os
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from sqlalchemy.engine import make_url

from backend import db


class DatabaseUrlFallbackTests(unittest.TestCase):
    def setUp(self):
        self._files_to_cleanup: list[Path] = []
        self._dirs_to_cleanup: list[Path] = []

    def tearDown(self):
        for path in self._files_to_cleanup:
            try:
                path.chmod(0o666)
            except Exception:
                pass
            try:
                path.unlink()
            except Exception:
                pass
        for d in self._dirs_to_cleanup:
            shutil.rmtree(d, ignore_errors=True)

    def test_readonly_sqlite_path_falls_back(self):
        temp_dir = Path(tempfile.mkdtemp())
        self._dirs_to_cleanup.append(temp_dir)

        original_db = temp_dir / "readonly.db"
        conn = sqlite3.connect(original_db)
        conn.execute("create table t(id int);")
        conn.commit()
        conn.close()

        original_db.chmod(0o444)
        self._files_to_cleanup.append(original_db)

        url = f"sqlite:///{original_db}"
        resolved = db._ensure_writable_sqlite_url(url)
        resolved_path = Path(make_url(resolved).database or "")

        self.assertNotEqual(url, resolved)
        self.assertTrue(resolved_path.exists())
        self.assertTrue(os.access(resolved_path, os.W_OK))

        if resolved_path != original_db:
            self._files_to_cleanup.append(resolved_path)

    def test_fallback_file_permissions_are_restrictive(self):
        """Test that fallback database files have restrictive permissions (0o600)."""
        temp_dir = Path(tempfile.mkdtemp())
        self._dirs_to_cleanup.append(temp_dir)

        original_db = temp_dir / "readonly.db"
        conn = sqlite3.connect(original_db)
        conn.execute("create table t(id int);")
        conn.commit()
        conn.close()

        original_db.chmod(0o444)
        self._files_to_cleanup.append(original_db)

        url = f"sqlite:///{original_db}"
        resolved = db._ensure_writable_sqlite_url(url)
        resolved_path = Path(make_url(resolved).database or "")

        if resolved_path != original_db:
            self._files_to_cleanup.append(resolved_path)
            # Check that the file permissions are 0o600 (owner read/write only)
            file_stat = resolved_path.stat()
            file_mode = file_stat.st_mode & 0o777
            self.assertEqual(file_mode, 0o600,
                           f"Expected file permissions 0o600, got {oct(file_mode)}")


if __name__ == "__main__":
    unittest.main()
