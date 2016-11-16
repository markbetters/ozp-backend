"""
Elasticsearch Utils tests

Test this class indiviual with command:
python manage.py test ozpcenter.api.listing.tests.test_elasticsearch_util
"""
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.api.listing import elasticsearch_util


class ElasticsearchUtilTest(TestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        pass

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def test_get_mapping_setting_obj(self):
        mapping_obj = elasticsearch_util.get_mapping_setting_obj()
        self.assertTrue('settings' in mapping_obj)

    # TODO Add more test
