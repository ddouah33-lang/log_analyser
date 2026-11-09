import unittest

from process.parser import parse_line
from process.analyzer import analyze

OK = "Nov  9 10:15:32 srv sshd[1234]: Accepted password for alice from 192.168.1.5 port 22 ssh2"
KO = "Nov  9 10:16:01 srv sshd[1235]: Failed password for root from 185.220.101.4 port 22 ssh2"
INV = "Nov  9 10:16:05 srv sshd[1236]: Failed password for invalid user admin from 185.220.101.4 port 22 ssh2"


class TestParser(unittest.TestCase):
    def test_success(self):
        e = parse_line(OK)
        self.assertTrue(e["success"])
        self.assertEqual(e["user"], "alice")

    def test_failed(self):
        self.assertFalse(parse_line(KO)["success"])

    def test_invalid_user(self):
        e = parse_line(INV)
        self.assertTrue(e["invalid_user"])
        self.assertEqual(e["user"], "admin")

    def test_bad_line(self):
        self.assertIsNone(parse_line("ligne n'importe quoi"))

    def test_bad_ip(self):
        bad = OK.replace("192.168.1.5", "999.1.1.1")
        self.assertIsNone(parse_line(bad))

    def test_analyze(self):
        events = [parse_line(x) for x in (OK, KO, INV)]
        res = analyze(events, {"185.220.": "Russie"})
        self.assertEqual(res["failed_by_country"], {"Russie": 2})
        self.assertEqual(res["success_by_user"], {"alice": 1})
        self.assertEqual(res["failed_invalid_user"], {"admin": 1})


if __name__ == "__main__":
    unittest.main()
