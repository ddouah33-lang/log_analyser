import unittest

from process.geolocation import is_valid_ip, is_private_ip, get_country

TABLE = {"185.220.": "Russie", "41.248.": "Maroc"}


class TestGeolocation(unittest.TestCase):
    def test_valid_ip(self):
        self.assertTrue(is_valid_ip("8.8.8.8"))
        self.assertFalse(is_valid_ip("999.1.1.1"))
        self.assertFalse(is_valid_ip("abc"))
        self.assertFalse(is_valid_ip(None))

    def test_private_ip(self):
        self.assertTrue(is_private_ip("192.168.1.5"))
        self.assertTrue(is_private_ip("10.0.0.1"))
        self.assertTrue(is_private_ip("172.20.0.1"))
        self.assertFalse(is_private_ip("172.32.0.1"))
        self.assertFalse(is_private_ip("8.8.8.8"))

    def test_country_found(self):
        self.assertEqual(get_country("185.220.101.4", TABLE), "Russie")

    def test_country_unknown(self):
        self.assertEqual(get_country("8.8.8.8", TABLE), "Inconnu")

    def test_private_country(self):
        self.assertEqual(get_country("192.168.1.5", TABLE), "Reseau local")

    def test_invalid_ip_country(self):
        self.assertEqual(get_country("999.1.1.1", TABLE), "Inconnu")
        self.assertEqual(get_country(None, TABLE), "Inconnu")


if __name__ == "__main__":
    unittest.main()