"""
Tests for image endpoints
"""
import unittest

from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

import ozpcenter.access_control as access_control

from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.api.agency.views as views
from ozpcenter import models as models
from ozpcenter import model_access as generic_model_access


class ImageApiTest(APITestCase):

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

    def test_post_image(self):
        pass
        # user = generic_model_access.get_profile('wsmith').user
        # self.client.force_authenticate(user=user)
        # url = '/api/image/'
        # data = {
        #     ''
        # }
        # response = self.client.post(url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertTrue('id' in response.data)

