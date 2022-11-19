import pytest


@pytest.mark.usefixtures('populate_db')
class TestDriverMethods:

    @pytest.mark.django_db
    def test_get_kassa(self, populate_db):
        assert populate_db.driver.get_kassa(vendor='Uber', week_number='2022-11-18') == 4500

    @pytest.mark.django_db
    def test_get_dynamic_rate(self, populate_db):
        assert populate_db.driver.get_dynamic_rate(vendor='Uber', week_number='2022-11-18') == 0.45

    @pytest.mark.django_db
    def test_get_salary(self, populate_db):
        assert populate_db.driver.get_salary(vendor='Uber', week_number='2022-11-18') == 1500


