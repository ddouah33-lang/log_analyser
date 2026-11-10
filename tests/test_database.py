import os
import unittest

from storage.database import get_connection, save_events, get_stats


class TestDatabase(unittest.TestCase):
    """Ces tests n'ont pas besoin d'une vraie base : ils verifient la gestion des erreurs."""

    def setUp(self):
        self.old_env = {k: os.environ.get(k) for k in ("DB_PASSWORD", "DB_PORT")}

    def tearDown(self):
        for key, value in self.old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_no_password(self):
        os.environ.pop("DB_PASSWORD", None)
        self.assertIsNone(get_connection())

    def test_bad_port(self):
        os.environ["DB_PASSWORD"] = "x"
        os.environ["DB_PORT"] = "abc"
        self.assertIsNone(get_connection())

    def test_connection_refused(self):
        os.environ["DB_PASSWORD"] = "x"
        os.environ["DB_PORT"] = "1"  # aucun serveur PostgreSQL sur ce port
        self.assertIsNone(get_connection())

    def test_save_without_database(self):
        os.environ.pop("DB_PASSWORD", None)
        self.assertFalse(save_events([], {}))

    def test_stats_without_database(self):
        os.environ.pop("DB_PASSWORD", None)
        self.assertEqual(get_stats(), {})


if __name__ == "__main__":
    unittest.main()
    