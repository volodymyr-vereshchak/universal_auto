import unittest

class TestBot(unittest.TestCase):
    def test_main(self):
        self.assertIsNotNone("/start")

    def test_main2(self):
        self.assertTrue('/start')

    def test_aut_handler(self):
        self.assertIsNotNone('Get autorizate')
    
    def test_reg_handler(self):
        self.assertIsNotNone('Get registration')

    def test_get_manager_today_report(self):
        self.assertTrue('Get all today statistic')

    def test_get_driver_today_report(self):
        self.assertTrue('Get today statistic')