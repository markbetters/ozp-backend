"""
Tests for Profile endpoints
"""
from unittest.mock import patch

from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase

from ozp.tests import helper
from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen


class ProfileApiTest(APITestCase):
    """
    Testing Profile API

    Users:
      aaronson (miniluv) - Aaronson - 6
      jones (minitrue) - Jones - 7
      rutherford (miniplenty) - Rutherford - 8
      syme (minipax) - Syme - 9
      tparsons (minipax, miniluv) - Tom Parsons - 10
      charrington (minipax, miniluv, minitrue) - Charrington - 11
    Org Stewards:
      wsmith (minitrue, stewarded_orgs: minitrue) - Winston Smith - 1
      julia (minitrue, stewarded_orgs: minitrue, miniluv) - Julia Dixon - 2
      obrien (minipax, stewarded_orgs: minipax, miniplenty) - O'brien - 3
    Admins:
      bigbrother (minipax) - Big Brother - 4
      bigbrother2 (minitrue) - Big Brother2 - 5
    """

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        # Store the orginal value of USE_AUTH_SERVER
        self.USE_AUTH_SERVER_ORGINAL = settings.OZP['USE_AUTH_SERVER']

    def tearDown(self):
        """
        tearDown is invoked after each test method
        """
        # Set the value of USE_AUTH_SERVER to the orginal value
        settings.OZP['USE_AUTH_SERVER'] = self.USE_AUTH_SERVER_ORGINAL

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def _all_listing_for_self_profile(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/self/listing/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [i['id'] for i in response.data]
        self.assertTrue(1 in ids)
        self.assertEquals(len(ids), 90)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_all_listing_for_self_profile_auth_enabled(self, mock_request):
        """
        Testing GET /api/profile/self/listing endpoint
        """
        # import plugins_util
        # print(dir(plugins_util.plugin_manager.plugin_manager_instance.default_authorization.requests.get))
        settings.OZP['USE_AUTH_SERVER'] = True
        self._all_listing_for_self_profile()

    def test_all_listing_for_self_profile_auth_disabled(self):
        """
        Testing GET /api/profile/self/listing endpoint
        """
        settings.OZP['USE_AUTH_SERVER'] = False
        self._all_listing_for_self_profile()

    def _one_listing_for_self_profile(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/self/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEquals(data['id'], 1)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_one_listing_for_self_profile_auth_enabled(self, mock_request):
        """
        Testing GET /api/profile/self/listing/{pk} endpoint
        """
        settings.OZP['USE_AUTH_SERVER'] = True
        self._one_listing_for_self_profile()

    def test_one_listing_for_self_profile_auth_disabled(self):
        """
        Testing GET /api/profile/self/listing/{pk} endpoint
        """
        settings.OZP['USE_AUTH_SERVER'] = False
        self._one_listing_for_self_profile()

    def _all_listing_for_minitrue_profile_from_multi_org_profile(self):
        user = generic_model_access.get_profile('charrington').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/4/listing/'
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [i['id'] for i in data]
        self.assertTrue(110 in ids)
        self.assertEquals(len(ids), 90)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_all_listing_for_minitrue_profile_from_multi_org_profile_auth_enabled(self, mock_request):
        """
        Testing GET /api/profile/1/listing/ endpoint

        Getting
            wsmith (minitrue, stewarded_orgs: minitrue) - Winston Smith - 4
        From
            charrington (minipax, miniluv, minitrue) - Charrington - 17
        """
        settings.OZP['USE_AUTH_SERVER'] = True
        self._all_listing_for_minitrue_profile_from_multi_org_profile()

    def test_all_listing_for_minitrue_profile_from_multi_org_profile_auth_disabled(self):
        """
        Testing GET /api/profile/1/listing/ endpoint

        Getting
            wsmith (minitrue, stewarded_orgs: minitrue) - Winston Smith - 4
        From
            charrington (minipax, miniluv, minitrue) - Charrington - 17
        """
        settings.OZP['USE_AUTH_SERVER'] = False
        self._all_listing_for_minitrue_profile_from_multi_org_profile()

    def _all_listing_for_app_profile_from_multi_org_profile(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/4/listing/'
        response = self.client.get(url, format='json')
        data = response.data
        # print(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        listing_unique_names = [i['unique_name'] for i in data]
        self.assertTrue('ozp.test.air_mail' in listing_unique_names)
        self.assertEquals(len(listing_unique_names), 90)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_all_listing_for_app_profile_from_multi_org_profile_auth_enabled(self, mock_request):
        """
        Testing GET /api/profile/4/listing/ endpoint

        Getting
            wsmith (minitrue, stewarded_orgs: minitrue) - Winston Smith - 4
        From
            bigbrother (minipax) - Big Brother - 1
        """
        settings.OZP['USE_AUTH_SERVER'] = True
        self._all_listing_for_app_profile_from_multi_org_profile()

    def test_all_listing_for_app_profile_from_multi_org_profile_auth_disabled(self):
        """
        Testing GET /api/profile/4/listing/ endpoint

        Getting
            wsmith (minitrue, stewarded_orgs: minitrue) - Winston Smith - 4
        From
            bigbrother (minipax) - Big Brother - 1
        """
        settings.OZP['USE_AUTH_SERVER'] = False
        self._all_listing_for_app_profile_from_multi_org_profile()

    def _all_listing_for_minitrue_profile_from_minitrue_profile(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/5/listing/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        listing_unique_names = [i['unique_name'] for i in data]
        self.assertTrue('ozp.test.chatterbox.8' in listing_unique_names)
        self.assertEquals(len(listing_unique_names), 10)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_all_listing_for_minitrue_profile_from_minitrue_profile(self, mock_request):
        """
        Testing GET /api/profile/5/listing/ endpoint

        Getting
            julia (minitrue, stewarded_orgs: minitrue, miniluv) - Julia Dixon - 5
        From
            jones (minitrue) - Jones - 9
        """
        settings.OZP['USE_AUTH_SERVER'] = True
        self._all_listing_for_minitrue_profile_from_minitrue_profile()

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_username_starts_with(self, mock_request):
        """
        Testing GET /api/profile/?username_starts_with={username} endpoint
        """
        settings.OZP['USE_AUTH_SERVER'] = True
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?username_starts_with=ws'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user']['username'], 'wsmith')

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_username_starts_with_no_results(self, mock_request):
        """
        Testing GET /api/profile/?username_starts_with={username} endpoint
        """
        settings.OZP['USE_AUTH_SERVER'] = True
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?username_starts_with=asdf'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_get_users_based_on_roles_for_all_access_control_levels(self, mock_request):
        """
        Testing GET /api/profile/?roles={role} endpoint
        """
        settings.OZP['USE_AUTH_SERVER'] = True
        roles_combos = {'APPS_MALL_STEWARD': [1, 0, 0],
                        'ORG_STEWARD': [0, 1, 0],
                        'USER': [0, 0, 1]}
        user_list = ['bigbrother',
                     'wsmith',
                     'jones']

        for role in roles_combos:
            combo = roles_combos[role]
            for current_username in user_list:
                # Get all '{role}' profiles at '{current_username}' access control level
                user = generic_model_access.get_profile(current_username).user
                self.client.force_authenticate(user=user)
                url = '/api/profile/?role={0!s}'.format(role)
                response = self.client.get(url, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                usernames = [i['user']['username'] for i in response.data]

                self.assertEquals('bigbrother' in usernames, bool(combo[0]), 'bigbrother role [{0!s}] in {1!s}'.format(role, bool(combo[0])))
                self.assertEquals('julia' in usernames, bool(combo[1]))
                self.assertEquals('jones' in usernames, bool(combo[2]))
                displaynames = [i['display_name'] for i in response.data]
                self.assertEqual(displaynames, sorted(displaynames))

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_get_update_self_for_all_access_control_levels(self, mock_request):
        """
        Testing GET/POST /api/self/profile endpoint
        """
        settings.OZP['USE_AUTH_SERVER'] = True
        # aaronson - 7
        # abe - 4
        # bigbrother - 1
        # bigbrother2 - 2
        # charrington - 17
        # khaleesi- 3
        # hodor - 8
        # johnson - 18
        # jsnow - 16
        # jones - 9
        # julia - 5
        # noah -12
        # obrien - 6
        # rutherford - 11
        # syme - 13
        # tammy - 10
        # tparsons - 15
        # wsmith - 4

        user_combo_list = [
            # bigbrother (minipax)
            {'id': 1, 'username': 'bigbrother', 'display_name': 'Big Brother',
                'stewarded_organizations': [],
                'groups': [{'name': 'APPS_MALL_STEWARD'}],
                'highest_role': 'APPS_MALL_STEWARD',
                'test_data_input_stewarded_organizations': False},
            # bigbrother2 (minitrue)
            {'id': 2, 'username': 'bigbrother2', 'display_name': 'Big Brother2',
                'stewarded_organizations': [],
                'groups': [{'name': 'APPS_MALL_STEWARD'}],
                'highest_role': 'APPS_MALL_STEWARD',
                'test_data_input_stewarded_organizations': False},
            # wsmith (minitrue, stewarded_orgs: minitrue) - Org Steward Level
            {'id': 4, 'username': 'wsmith', 'display_name': 'Winston Smith',
                'stewarded_organizations': [{"short_name": "Minitrue", "title": "Ministry of Truth"}],
                'groups': [{"name": "ORG_STEWARD"}],
                'highest_role': 'ORG_STEWARD',
                'test_data_input_stewarded_organizations': True},
            # charrington (minipax, miniluv, minitrue) - User Level
            {'id': 19, 'username': 'charrington', 'display_name': 'Charrington',
                'stewarded_organizations': [],
                'groups': [{'name': 'USER'}],
                'highest_role': 'USER',
                'test_data_input_stewarded_organizations': True},
            # jones (minitrue) - User Level
            {'id': 11,
                'username': 'jones',
                'display_name': 'Jones',
                'stewarded_organizations': [],
                'groups': [{'name': 'USER'}],
                'highest_role': 'USER',
                'test_data_input_stewarded_organizations': True}
        ]

        for current_user_info in user_combo_list:
            current_id = current_user_info['id']
            current_username = current_user_info['username']
            current_display_name = current_user_info['display_name']
            current_stewarded_organizations = current_user_info['stewarded_organizations']
            current_groups = current_user_info['groups']
            current_highest_role = current_user_info['highest_role']
            current_test_data_input_stewarded_organizations = current_user_info['test_data_input_stewarded_organizations']

            user = generic_model_access.get_profile(current_username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/profile/'
            response = self.client.get(url, format='json')
            response_username = response.data.get('user').get('username')
            response_id = response.data.get('id')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data.get('id'), current_id, '{}: Actual ID: {} Expected ID: {}'.format(response_username, response_id, current_id))
            self.assertEqual(response.data.get('display_name'), current_display_name)
            self.assertEqual(response.data.get('stewarded_organizations'), current_stewarded_organizations)
            self.assertEqual(response_username, current_username)
            self.assertEqual(response.data.get('user').get('groups'), current_groups)
            self.assertEqual(response.data.get('highest_role'), current_highest_role)
            self.assertEqual(response.data.get('center_tour_flag'), True)
            self.assertEqual(response.data.get('hud_tour_flag'), True)
            self.assertEqual(response.data.get('webtop_tour_flag'), True)

            combinations = [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1],
                            [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]

            # This loop is testing for all possible flags combinations
            for combination in combinations:
                center_tour_flag = bool(combination[0])
                hud_tour_flag = bool(combination[1])
                webtop_tour_flag = bool(combination[2])

                data = {'id': -1,
                        'center_tour_flag': center_tour_flag,
                        'hud_tour_flag': hud_tour_flag,
                        'webtop_tour_flag': webtop_tour_flag}

                # Testing to make sure that profiles that are lower than
                # APP Mall Steward profile can't edit the stewarded_organizations
                if current_test_data_input_stewarded_organizations:
                    data['stewarded_organizations'] = [{'title': 'Ministry of Truth'},
                                                       {'title': 'Ministry of Love'}]

                response = self.client.put(url, data, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data.get('id'), current_id)
                self.assertEqual(response.data.get('display_name'), current_display_name)
                self.assertEqual(response.data.get('stewarded_organizations'), current_stewarded_organizations)
                self.assertEqual(response.data.get('user').get('username'), current_username)
                self.assertEqual(response.data.get('user').get('groups'), current_groups)
                self.assertEqual(response.data.get('highest_role'), current_highest_role)
                self.assertEqual(response.data.get('center_tour_flag'), center_tour_flag)
                self.assertEqual(response.data.get('hud_tour_flag'), hud_tour_flag)
                self.assertEqual(response.data.get('webtop_tour_flag'), webtop_tour_flag)

                response = self.client.get(url, format='json')
                self.assertEqual(response.data.get('center_tour_flag'), center_tour_flag)
                self.assertEqual(response.data.get('hud_tour_flag'), hud_tour_flag)
                self.assertEqual(response.data.get('webtop_tour_flag'), webtop_tour_flag)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_update_self_for_apps_mall_steward_level_serializer_exception(self, mock_request):
        """
        Testing POST /api/self/profile endpoint - serializer exception
        """
        settings.OZP['USE_AUTH_SERVER'] = True
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/self/profile/'
        data = {'id': 5, 'center_tour_flag': 4}
        response = self.client.put(url, data, format='json')

        expected_data = {'center_tour_flag': ['"4" is not a valid boolean.']}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_update_self_for_apps_mall_steward_level_invalid_user(self, mock_request):
        """
        Testing POST /api/self/profile endpoint - invalid user
        """
        settings.OZP['USE_AUTH_SERVER'] = True
        url = '/api/self/profile/'
        data = {'id': 5, 'center_tour_flag': False}
        self.client.login(username='invalid', password='invalid')
        response = self.client.put(url, data, format='json')

        expected_data = {'detail': 'Authentication credentials were not provided.', 'error': True}
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, expected_data)

    def _get_profile_url_for_username(self, username):
        """
        Get Profile Url
        """
        user_id = generic_model_access.get_profile(username).user.id
        return '/api/profile/{}/'.format(user_id)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_update_stewarded_orgs_for_apps_mall_steward_level(self, mock_request):
        settings.OZP['USE_AUTH_SERVER'] = True
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/1/'
        data = {'display_name': 'Winston Smith', 'stewarded_organizations': [
               {'title': 'Ministry of Truth'}, {'title': 'Ministry of Love'}]}
        response = self.client.put(url, data, format='json')

        orgs = [i['title'] for i in response.data.get('stewarded_organizations')]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('Ministry of Truth' in orgs)
        self.assertTrue('Ministry of Love' in orgs)
        self.assertEqual(len(orgs), 2)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_update_stewarded_orgs_for_apps_mall_steward_level_serializer_exception(self, mock_request):
        settings.OZP['USE_AUTH_SERVER'] = True
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = self._get_profile_url_for_username('wsmith')
        data = {'display_name': 'Winston Smith', 'stewarded_organizations': False}
        response = self.client.put(url, data, format='json')

        expected_data = {'stewarded_organizations': {'non_field_errors': ['Expected a list of items but got type "bool".']}}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected_data)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_update_stewarded_orgs_for_org_steward_level(self, mock_request):
        settings.OZP['USE_AUTH_SERVER'] = True
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = self._get_profile_url_for_username('wsmith')
        data = {'display_name': 'Winston Smith', 'stewarded_organizations': [
               {'title': 'Ministry of Truth'}, {'title': 'Ministry of Love'}]}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('plugins_util.plugin_manager.requests.get', side_effect=helper.mocked_requests_get)
    def test_update_stewarded_orgs_for_user_level(self, mock_request):
        settings.OZP['USE_AUTH_SERVER'] = True
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = self._get_profile_url_for_username('wsmith')
        data = {'display_name': 'Winston Smith', 'stewarded_organizations': [
               {'title': 'Ministry of Truth'}, {'title': 'Ministry of Love'}]}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
