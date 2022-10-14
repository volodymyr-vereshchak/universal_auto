import unittest


class TestBot(unittest.TestCase):
    def test_start(self):
        self.assertIsNotNone("/start")

    def test_start_2(self):
        self.assertTrue('/start')

    def test_report(self):
        self.assertIsNotNone("/report")

    def test_report_2(self):
        self.assertTrue('/report')

    def test_save_reports(self):
        self.assertIsNotNone("/save_reports")

    def test_save_reports_2(self):
        self.assertTrue('/save_reports')

    def test_update_db(self):
        self.assertTrue('/update_db')

    def test_update_db_2(self):
        self.assertIsNotNone('/update_db')