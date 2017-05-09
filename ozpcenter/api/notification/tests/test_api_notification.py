"""
Tests for notification endpoints
"""
from unittest import skip
import copy
import datetime
import pytz

from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.api.library.tests.test_api_library import _create_create_bookmark


def _import_bookmarks(test_case_instance, username, bookmark_notification_id, status_code=201):
    user = generic_model_access.get_profile(username).user
    test_case_instance.client.force_authenticate(user=user)
    url = '/api/self/library/import_bookmarks/'
    data = {'bookmark_notification_id': bookmark_notification_id}
    response = test_case_instance.client.post(url, data, format='json')

    if response:
        if status_code == 201:
            test_case_instance.assertEqual(response.status_code, status.HTTP_201_CREATED)
        elif status_code == 400:
            test_case_instance.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:
            raise Exception('status code is not supported')

    return response


class NotificationApiTest(APITestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        self

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def test_get_self_notification(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for current_notification in response.data:
            self.assertIn('id', current_notification)
            self.assertIn('created_date', current_notification)
            self.assertIn('expires_date', current_notification)
            self.assertIn('message', current_notification)
            self.assertIn('author', current_notification)
            self.assertIn('listing', current_notification)
            self.assertIn('agency', current_notification)
            self.assertIn('notification_type', current_notification)
            self.assertIn('peer', current_notification)

    def test_get_self_notification_unauthorized(self):
        url = '/api/self/notification/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_self_notification_ordering(self):
        # Get default
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification_list = ['{}-{}-{}'.format(entry['entity_id'], entry['notification_type'], ''.join(entry['message'].split())) for entry in response.data]
        expected_data = ['11-listing-BreadBasketupdatenextweek',
                         '112-listing-Skybox1updatenextweek',
                         '1-listing-AirMailupdatenextweek',
                         '114-listing-Skybox3updatenextweek',
                         '113-listing-Skybox2updatenextweek',
                         '112-listing-Skybox1updatenextweek',
                         '1-listing-AirMailupdatenextweek',
                         '11-listing-BreadBasketupdatenextweek',
                         '90-listing-Userhasratedlisting[LocationLister9]4stars',
                         '89-listing-Userhasratedlisting[LocationLister8]4stars',
                         '88-listing-Userhasratedlisting[LocationLister7]4stars',
                         '87-listing-Userhasratedlisting[LocationLister6]4stars',
                         '86-listing-Userhasratedlisting[LocationLister5]4stars',
                         '85-listing-Userhasratedlisting[LocationLister4]4stars',
                         '84-listing-Userhasratedlisting[LocationLister3]4stars',
                         '83-listing-Userhasratedlisting[LocationLister2]4stars',
                         '82-listing-Userhasratedlisting[LocationLister1]4stars',
                         '81-listing-Userhasratedlisting[LocationLister]4stars',
                         '80-listing-Userhasratedlisting[JotSpot9]4stars',
                         '78-listing-Userhasratedlisting[JotSpot8]4stars',
                         '76-listing-Userhasratedlisting[JotSpot7]4stars',
                         '74-listing-Userhasratedlisting[JotSpot6]4stars',
                         '72-listing-Userhasratedlisting[JotSpot5]4stars',
                         '70-listing-Userhasratedlisting[JotSpot4]4stars',
                         '68-listing-Userhasratedlisting[JotSpot3]4stars',
                         '66-listing-Userhasratedlisting[JotSpot2]4stars',
                         '64-listing-Userhasratedlisting[JotSpot1]4stars',
                         '62-listing-Userhasratedlisting[JotSpot]4stars',
                         '30-listing-Userhasratedlisting[ChartCourse9]5stars',
                         '30-listing-Userhasratedlisting[ChartCourse9]2stars',
                         '29-listing-Userhasratedlisting[ChartCourse8]5stars',
                         '29-listing-Userhasratedlisting[ChartCourse8]2stars',
                         '28-listing-Userhasratedlisting[ChartCourse7]5stars',
                         '28-listing-Userhasratedlisting[ChartCourse7]2stars',
                         '27-listing-Userhasratedlisting[ChartCourse6]5stars',
                         '27-listing-Userhasratedlisting[ChartCourse6]2stars',
                         '26-listing-Userhasratedlisting[ChartCourse5]5stars',
                         '26-listing-Userhasratedlisting[ChartCourse5]2stars',
                         '25-listing-Userhasratedlisting[ChartCourse4]5stars',
                         '25-listing-Userhasratedlisting[ChartCourse4]2stars',
                         '24-listing-Userhasratedlisting[ChartCourse3]5stars',
                         '24-listing-Userhasratedlisting[ChartCourse3]2stars',
                         '23-listing-Userhasratedlisting[ChartCourse2]5stars',
                         '23-listing-Userhasratedlisting[ChartCourse2]2stars',
                         '22-listing-Userhasratedlisting[ChartCourse1]5stars',
                         '22-listing-Userhasratedlisting[ChartCourse1]2stars',
                         '21-listing-Userhasratedlisting[ChartCourse]5stars',
                         '21-listing-Userhasratedlisting[ChartCourse]2stars',
                         '20-listing-Userhasratedlisting[BreadBasket9]5stars',
                         '20-listing-Userhasratedlisting[BreadBasket9]2stars',
                         '19-listing-Userhasratedlisting[BreadBasket8]5stars',
                         '19-listing-Userhasratedlisting[BreadBasket8]2stars',
                         '18-listing-Userhasratedlisting[BreadBasket7]5stars',
                         '18-listing-Userhasratedlisting[BreadBasket7]2stars',
                         '17-listing-Userhasratedlisting[BreadBasket6]5stars',
                         '17-listing-Userhasratedlisting[BreadBasket6]2stars',
                         '16-listing-Userhasratedlisting[BreadBasket5]5stars',
                         '16-listing-Userhasratedlisting[BreadBasket5]2stars',
                         '15-listing-Userhasratedlisting[BreadBasket4]5stars',
                         '15-listing-Userhasratedlisting[BreadBasket4]2stars',
                         '14-listing-Userhasratedlisting[BreadBasket3]5stars',
                         '14-listing-Userhasratedlisting[BreadBasket3]2stars',
                         '13-listing-Userhasratedlisting[BreadBasket2]5stars',
                         '13-listing-Userhasratedlisting[BreadBasket2]2stars',
                         '12-listing-Userhasratedlisting[BreadBasket1]5stars',
                         '12-listing-Userhasratedlisting[BreadBasket1]2stars',
                         '11-listing-Userhasratedlisting[BreadBasket]5stars',
                         '11-listing-Userhasratedlisting[BreadBasket]2stars',
                         '10-listing-Userhasratedlisting[AirMail9]1stars',
                         '10-listing-Userhasratedlisting[AirMail9]3stars',
                         '10-listing-Userhasratedlisting[AirMail9]5stars',
                         '9-listing-Userhasratedlisting[AirMail8]1stars',
                         '9-listing-Userhasratedlisting[AirMail8]3stars',
                         '9-listing-Userhasratedlisting[AirMail8]5stars',
                         '8-listing-Userhasratedlisting[AirMail7]1stars',
                         '8-listing-Userhasratedlisting[AirMail7]3stars',
                         '8-listing-Userhasratedlisting[AirMail7]5stars',
                         '7-listing-Userhasratedlisting[AirMail6]1stars',
                         '7-listing-Userhasratedlisting[AirMail6]3stars',
                         '7-listing-Userhasratedlisting[AirMail6]5stars',
                         '6-listing-Userhasratedlisting[AirMail5]1stars',
                         '6-listing-Userhasratedlisting[AirMail5]3stars',
                         '6-listing-Userhasratedlisting[AirMail5]5stars',
                         '5-listing-Userhasratedlisting[AirMail4]1stars',
                         '5-listing-Userhasratedlisting[AirMail4]3stars',
                         '5-listing-Userhasratedlisting[AirMail4]5stars',
                         '4-listing-Userhasratedlisting[AirMail3]1stars',
                         '4-listing-Userhasratedlisting[AirMail3]3stars',
                         '4-listing-Userhasratedlisting[AirMail3]5stars',
                         '3-listing-Userhasratedlisting[AirMail2]1stars',
                         '3-listing-Userhasratedlisting[AirMail2]3stars',
                         '3-listing-Userhasratedlisting[AirMail2]5stars',
                         '2-listing-Userhasratedlisting[AirMail1]1stars',
                         '2-listing-Userhasratedlisting[AirMail1]3stars',
                         '2-listing-Userhasratedlisting[AirMail1]5stars',
                         '1-listing-Userhasratedlisting[AirMail]1stars',
                         '1-listing-Userhasratedlisting[AirMail]3stars',
                         '1-listing-Userhasratedlisting[AirMail]5stars',
                         'None-system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                         'None-system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']

        self.assertEqual(notification_list, expected_data)

        # Get reversed order
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/?ordering=-created_date'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification_list = ['{}-{}-{}'.format(entry['entity_id'], entry['notification_type'], ''.join(entry['message'].split())) for entry in response.data]

        self.assertEqual(notification_list, expected_data)

        # Get ascending order
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/?ordering=created_date'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification_list = ['{}-{}-{}'.format(entry['entity_id'], entry['notification_type'], ''.join(entry['message'].split())) for entry in response.data]
        self.assertEqual(notification_list, list(reversed(expected_data)))

    def test_dismiss_self_notification(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append([i['id'], ''.join(i['message'].split())])

        expected = [[106, 'BreadBasketupdatenextweek'],
                    [105, 'Skybox1updatenextweek'],
                    [103, 'AirMailupdatenextweek'],
                    [99, 'Skybox3updatenextweek'],
                    [98, 'Skybox2updatenextweek'],
                    [97, 'Skybox1updatenextweek'],
                    [96, 'AirMailupdatenextweek'],
                    [95, 'BreadBasketupdatenextweek'],
                    [94, 'Userhasratedlisting[LocationLister9]4stars'],
                    [93, 'Userhasratedlisting[LocationLister8]4stars'],
                    [92, 'Userhasratedlisting[LocationLister7]4stars'],
                    [91, 'Userhasratedlisting[LocationLister6]4stars'],
                    [90, 'Userhasratedlisting[LocationLister5]4stars'],
                    [89, 'Userhasratedlisting[LocationLister4]4stars'],
                    [88, 'Userhasratedlisting[LocationLister3]4stars'],
                    [87, 'Userhasratedlisting[LocationLister2]4stars'],
                    [86, 'Userhasratedlisting[LocationLister1]4stars'],
                    [85, 'Userhasratedlisting[LocationLister]4stars'],
                    [84, 'Userhasratedlisting[JotSpot9]4stars'],
                    [83, 'Userhasratedlisting[JotSpot8]4stars'],
                    [82, 'Userhasratedlisting[JotSpot7]4stars'],
                    [81, 'Userhasratedlisting[JotSpot6]4stars'],
                    [80, 'Userhasratedlisting[JotSpot5]4stars'],
                    [79, 'Userhasratedlisting[JotSpot4]4stars'],
                    [78, 'Userhasratedlisting[JotSpot3]4stars'],
                    [77, 'Userhasratedlisting[JotSpot2]4stars'],
                    [76, 'Userhasratedlisting[JotSpot1]4stars'],
                    [75, 'Userhasratedlisting[JotSpot]4stars'],
                    [74, 'Userhasratedlisting[ChartCourse9]5stars'],
                    [73, 'Userhasratedlisting[ChartCourse9]2stars'],
                    [72, 'Userhasratedlisting[ChartCourse8]5stars'],
                    [71, 'Userhasratedlisting[ChartCourse8]2stars'],
                    [70, 'Userhasratedlisting[ChartCourse7]5stars'],
                    [69, 'Userhasratedlisting[ChartCourse7]2stars'],
                    [68, 'Userhasratedlisting[ChartCourse6]5stars'],
                    [67, 'Userhasratedlisting[ChartCourse6]2stars'],
                    [66, 'Userhasratedlisting[ChartCourse5]5stars'],
                    [65, 'Userhasratedlisting[ChartCourse5]2stars'],
                    [64, 'Userhasratedlisting[ChartCourse4]5stars'],
                    [63, 'Userhasratedlisting[ChartCourse4]2stars'],
                    [62, 'Userhasratedlisting[ChartCourse3]5stars'],
                    [61, 'Userhasratedlisting[ChartCourse3]2stars'],
                    [60, 'Userhasratedlisting[ChartCourse2]5stars'],
                    [59, 'Userhasratedlisting[ChartCourse2]2stars'],
                    [58, 'Userhasratedlisting[ChartCourse1]5stars'],
                    [57, 'Userhasratedlisting[ChartCourse1]2stars'],
                    [56, 'Userhasratedlisting[ChartCourse]5stars'],
                    [55, 'Userhasratedlisting[ChartCourse]2stars'],
                    [54, 'Userhasratedlisting[BreadBasket9]5stars'],
                    [53, 'Userhasratedlisting[BreadBasket9]2stars'],
                    [52, 'Userhasratedlisting[BreadBasket8]5stars'],
                    [51, 'Userhasratedlisting[BreadBasket8]2stars'],
                    [50, 'Userhasratedlisting[BreadBasket7]5stars'],
                    [49, 'Userhasratedlisting[BreadBasket7]2stars'],
                    [48, 'Userhasratedlisting[BreadBasket6]5stars'],
                    [47, 'Userhasratedlisting[BreadBasket6]2stars'],
                    [46, 'Userhasratedlisting[BreadBasket5]5stars'],
                    [45, 'Userhasratedlisting[BreadBasket5]2stars'],
                    [44, 'Userhasratedlisting[BreadBasket4]5stars'],
                    [43, 'Userhasratedlisting[BreadBasket4]2stars'],
                    [42, 'Userhasratedlisting[BreadBasket3]5stars'],
                    [41, 'Userhasratedlisting[BreadBasket3]2stars'],
                    [40, 'Userhasratedlisting[BreadBasket2]5stars'],
                    [39, 'Userhasratedlisting[BreadBasket2]2stars'],
                    [38, 'Userhasratedlisting[BreadBasket1]5stars'],
                    [37, 'Userhasratedlisting[BreadBasket1]2stars'],
                    [36, 'Userhasratedlisting[BreadBasket]5stars'],
                    [35, 'Userhasratedlisting[BreadBasket]2stars'],
                    [34, 'Userhasratedlisting[AirMail9]1stars'],
                    [33, 'Userhasratedlisting[AirMail9]3stars'],
                    [32, 'Userhasratedlisting[AirMail9]5stars'],
                    [31, 'Userhasratedlisting[AirMail8]1stars'],
                    [30, 'Userhasratedlisting[AirMail8]3stars'],
                    [29, 'Userhasratedlisting[AirMail8]5stars'],
                    [28, 'Userhasratedlisting[AirMail7]1stars'],
                    [27, 'Userhasratedlisting[AirMail7]3stars'],
                    [26, 'Userhasratedlisting[AirMail7]5stars'],
                    [25, 'Userhasratedlisting[AirMail6]1stars'],
                    [24, 'Userhasratedlisting[AirMail6]3stars'],
                    [23, 'Userhasratedlisting[AirMail6]5stars'],
                    [22, 'Userhasratedlisting[AirMail5]1stars'],
                    [21, 'Userhasratedlisting[AirMail5]3stars'],
                    [20, 'Userhasratedlisting[AirMail5]5stars'],
                    [19, 'Userhasratedlisting[AirMail4]1stars'],
                    [18, 'Userhasratedlisting[AirMail4]3stars'],
                    [17, 'Userhasratedlisting[AirMail4]5stars'],
                    [16, 'Userhasratedlisting[AirMail3]1stars'],
                    [15, 'Userhasratedlisting[AirMail3]3stars'],
                    [14, 'Userhasratedlisting[AirMail3]5stars'],
                    [13, 'Userhasratedlisting[AirMail2]1stars'],
                    [12, 'Userhasratedlisting[AirMail2]3stars'],
                    [11, 'Userhasratedlisting[AirMail2]5stars'],
                    [10, 'Userhasratedlisting[AirMail1]1stars'],
                    [9, 'Userhasratedlisting[AirMail1]3stars'],
                    [8, 'Userhasratedlisting[AirMail1]5stars'],
                    [7, 'Userhasratedlisting[AirMail]1stars'],
                    [6, 'Userhasratedlisting[AirMail]3stars'],
                    [5, 'Userhasratedlisting[AirMail]5stars'],
                    [2, 'Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B'],
                    [1, 'Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']]

        self.assertEqual(expected, notification_ids)

        # now dismiss the first notification
        dismissed_notification_id = notification_ids[0][0]
        url = url + str(dismissed_notification_id) + '/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # now get our notifications again, make sure the one was removed
        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append([i['id'], ''.join(i['message'].split())])

        expected = [[105, 'Skybox1updatenextweek'],
                    [103, 'AirMailupdatenextweek'],
                    [99, 'Skybox3updatenextweek'],
                    [98, 'Skybox2updatenextweek'],
                    [97, 'Skybox1updatenextweek'],
                    [96, 'AirMailupdatenextweek'],
                    [95, 'BreadBasketupdatenextweek'],
                    [94, 'Userhasratedlisting[LocationLister9]4stars'],
                    [93, 'Userhasratedlisting[LocationLister8]4stars'],
                    [92, 'Userhasratedlisting[LocationLister7]4stars'],
                    [91, 'Userhasratedlisting[LocationLister6]4stars'],
                    [90, 'Userhasratedlisting[LocationLister5]4stars'],
                    [89, 'Userhasratedlisting[LocationLister4]4stars'],
                    [88, 'Userhasratedlisting[LocationLister3]4stars'],
                    [87, 'Userhasratedlisting[LocationLister2]4stars'],
                    [86, 'Userhasratedlisting[LocationLister1]4stars'],
                    [85, 'Userhasratedlisting[LocationLister]4stars'],
                    [84, 'Userhasratedlisting[JotSpot9]4stars'],
                    [83, 'Userhasratedlisting[JotSpot8]4stars'],
                    [82, 'Userhasratedlisting[JotSpot7]4stars'],
                    [81, 'Userhasratedlisting[JotSpot6]4stars'],
                    [80, 'Userhasratedlisting[JotSpot5]4stars'],
                    [79, 'Userhasratedlisting[JotSpot4]4stars'],
                    [78, 'Userhasratedlisting[JotSpot3]4stars'],
                    [77, 'Userhasratedlisting[JotSpot2]4stars'],
                    [76, 'Userhasratedlisting[JotSpot1]4stars'],
                    [75, 'Userhasratedlisting[JotSpot]4stars'],
                    [74, 'Userhasratedlisting[ChartCourse9]5stars'],
                    [73, 'Userhasratedlisting[ChartCourse9]2stars'],
                    [72, 'Userhasratedlisting[ChartCourse8]5stars'],
                    [71, 'Userhasratedlisting[ChartCourse8]2stars'],
                    [70, 'Userhasratedlisting[ChartCourse7]5stars'],
                    [69, 'Userhasratedlisting[ChartCourse7]2stars'],
                    [68, 'Userhasratedlisting[ChartCourse6]5stars'],
                    [67, 'Userhasratedlisting[ChartCourse6]2stars'],
                    [66, 'Userhasratedlisting[ChartCourse5]5stars'],
                    [65, 'Userhasratedlisting[ChartCourse5]2stars'],
                    [64, 'Userhasratedlisting[ChartCourse4]5stars'],
                    [63, 'Userhasratedlisting[ChartCourse4]2stars'],
                    [62, 'Userhasratedlisting[ChartCourse3]5stars'],
                    [61, 'Userhasratedlisting[ChartCourse3]2stars'],
                    [60, 'Userhasratedlisting[ChartCourse2]5stars'],
                    [59, 'Userhasratedlisting[ChartCourse2]2stars'],
                    [58, 'Userhasratedlisting[ChartCourse1]5stars'],
                    [57, 'Userhasratedlisting[ChartCourse1]2stars'],
                    [56, 'Userhasratedlisting[ChartCourse]5stars'],
                    [55, 'Userhasratedlisting[ChartCourse]2stars'],
                    [54, 'Userhasratedlisting[BreadBasket9]5stars'],
                    [53, 'Userhasratedlisting[BreadBasket9]2stars'],
                    [52, 'Userhasratedlisting[BreadBasket8]5stars'],
                    [51, 'Userhasratedlisting[BreadBasket8]2stars'],
                    [50, 'Userhasratedlisting[BreadBasket7]5stars'],
                    [49, 'Userhasratedlisting[BreadBasket7]2stars'],
                    [48, 'Userhasratedlisting[BreadBasket6]5stars'],
                    [47, 'Userhasratedlisting[BreadBasket6]2stars'],
                    [46, 'Userhasratedlisting[BreadBasket5]5stars'],
                    [45, 'Userhasratedlisting[BreadBasket5]2stars'],
                    [44, 'Userhasratedlisting[BreadBasket4]5stars'],
                    [43, 'Userhasratedlisting[BreadBasket4]2stars'],
                    [42, 'Userhasratedlisting[BreadBasket3]5stars'],
                    [41, 'Userhasratedlisting[BreadBasket3]2stars'],
                    [40, 'Userhasratedlisting[BreadBasket2]5stars'],
                    [39, 'Userhasratedlisting[BreadBasket2]2stars'],
                    [38, 'Userhasratedlisting[BreadBasket1]5stars'],
                    [37, 'Userhasratedlisting[BreadBasket1]2stars'],
                    [36, 'Userhasratedlisting[BreadBasket]5stars'],
                    [35, 'Userhasratedlisting[BreadBasket]2stars'],
                    [34, 'Userhasratedlisting[AirMail9]1stars'],
                    [33, 'Userhasratedlisting[AirMail9]3stars'],
                    [32, 'Userhasratedlisting[AirMail9]5stars'],
                    [31, 'Userhasratedlisting[AirMail8]1stars'],
                    [30, 'Userhasratedlisting[AirMail8]3stars'],
                    [29, 'Userhasratedlisting[AirMail8]5stars'],
                    [28, 'Userhasratedlisting[AirMail7]1stars'],
                    [27, 'Userhasratedlisting[AirMail7]3stars'],
                    [26, 'Userhasratedlisting[AirMail7]5stars'],
                    [25, 'Userhasratedlisting[AirMail6]1stars'],
                    [24, 'Userhasratedlisting[AirMail6]3stars'],
                    [23, 'Userhasratedlisting[AirMail6]5stars'],
                    [22, 'Userhasratedlisting[AirMail5]1stars'],
                    [21, 'Userhasratedlisting[AirMail5]3stars'],
                    [20, 'Userhasratedlisting[AirMail5]5stars'],
                    [19, 'Userhasratedlisting[AirMail4]1stars'],
                    [18, 'Userhasratedlisting[AirMail4]3stars'],
                    [17, 'Userhasratedlisting[AirMail4]5stars'],
                    [16, 'Userhasratedlisting[AirMail3]1stars'],
                    [15, 'Userhasratedlisting[AirMail3]3stars'],
                    [14, 'Userhasratedlisting[AirMail3]5stars'],
                    [13, 'Userhasratedlisting[AirMail2]1stars'],
                    [12, 'Userhasratedlisting[AirMail2]3stars'],
                    [11, 'Userhasratedlisting[AirMail2]5stars'],
                    [10, 'Userhasratedlisting[AirMail1]1stars'],
                    [9, 'Userhasratedlisting[AirMail1]3stars'],
                    [8, 'Userhasratedlisting[AirMail1]5stars'],
                    [7, 'Userhasratedlisting[AirMail]1stars'],
                    [6, 'Userhasratedlisting[AirMail]3stars'],
                    [5, 'Userhasratedlisting[AirMail]5stars'],
                    [2, 'Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B'],
                    [1, 'Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']]

        self.assertEqual(expected, notification_ids)

    def test_get_pending_notifications(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/pending/'
        response = self.client.get(url, format='json')

        expires_at = [i['expires_date'] for i in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(expires_at) > 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time > now)

    def test_get_pending_notifications_user_unauthorized(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/pending/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_pending_notifications_listing_filter(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/pending/?listing=1'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification_list = [['{}-{}-{}'.format(entry['entity_id'], entry['notification_type'], ''.join(entry['message'].split())), entry['expires_date']] for entry in response.data]
        expected = ['1-listing-Userhasratedlisting[AirMail]5stars',
                    '1-listing-Userhasratedlisting[AirMail]3stars',
                    '1-listing-Userhasratedlisting[AirMail]1stars',
                    '1-listing-AirMailupdatenextweek',
                    '1-listing-AirMailupdatenextweek']

        self.assertEqual(expected, [entry[0] for entry in notification_list])

        now = datetime.datetime.now(pytz.utc)
        expires_at = [entry[1] for entry in notification_list]
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time > now)

    def test_all_pending_notifications_listing_filter_user_unauthorized(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/pending/?listing=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_expired_notifications(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/expired/'
        response = self.client.get(url, format='json')

        expires_at = [i['expires_date'] for i in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(expires_at) > 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time < now)

    def test_get_expired_notifications_user_unauthorized(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/expired/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO should work when data script gets refactored (rivera 20160620)
    @skip("should work when data script gets refactored (rivera 20160620)")
    def test_all_expired_notifications_listing_filter(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/expired/?listing=1'
        response = self.client.get(url, format='json')

        ids = [i['id'] for i in response.data]
        expires_at = [i['expires_date'] for i in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ids, [1])
        self.assertTrue(len(expires_at) == 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time < now)

    def test_all_expired_notifications_listing_filter_user_unauthorized(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/expired/?listing=1'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO: test_all_notifications_listing_filter (rivera 20160617)

    def test_create_system_notification(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        data = {'expires_date': '2016-09-01T15:45:55.322421Z',
                'message': 'a simple test'}

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'a simple test')
        self.assertEqual(response.data['notification_type'], 'system')

    def test_create_system_notification_unauthorized_user(self):
        # test_create_system_notification_unauthorized_user
        # test unauthorized user - only org stewards and above can create
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        data = {'expires_date': '2016-09-01T15:45:55.322421Z',
                'message': 'a simple test'}
        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_system_notification(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now)}
        url = '/api/notification/1/'
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # TODO: Verify expires_date

    def test_update_system_notification_unauthorized_user(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now)}
        url = '/api/notification/1/'
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO below test should work when permission gets refactored (rivera 20160620)
    @skip("should work permissions gets refactored (rivera 20160620)")
    def test_update_system_notification_unauthorized_org_steward(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now)}
        url = '/api/notification/1/'
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_listing_notification_app_mall_steward(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {
            'id': 1
            }}
        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'a simple listing test')
        self.assertEqual(response.data['notification_type'], 'listing')
        self.assertEqual(response.data['listing']['id'], 1)
        self.assertEqual(response.data['agency'], None)
        self.assertTrue('expires_date' in data)

    def test_create_listing_notification_app_mall_steward_invalid_format(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'invalid': 1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Valid Listing ID is required'])

    def test_create_listing_notification_app_mall_steward_invalid_id(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'id': -1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Could not find listing'])

    def test_create_listing_agency_notification_app_mall_steward_invalid(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'id': 1},
                'agency': {'id': 1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ["Notifications can only be one type. Input: ['listing', 'agency']"])

    def test_create_listing_notification_org_steward(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'id': 1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'a simple listing test')
        self.assertEqual(response.data['notification_type'], 'listing')
        self.assertEqual(response.data['listing']['id'], 1)
        self.assertEqual(response.data['agency'], None)
        self.assertTrue('expires_date' in data)

    def test_create_listing_notification_org_steward_invalid_format(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'invalid': 1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ["Valid Listing ID is required"])

    def test_create_listing_notification_org_steward_invalid_id(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'id': -1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ["Could not find listing"])

    # TODO: test_create_listing_notification_org_steward_invalid (rivera 20160617)
    # TODO: test_create_listing_notification_user_unauthorized (rivera 20160617)

    def test_create_agency_notification_app_mall_steward(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'A Simple Agency Test',
                'agency': {'id': 1}
                }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'A Simple Agency Test')
        self.assertEqual(response.data['notification_type'], 'agency')
        self.assertEqual(response.data['agency']['id'], 1)
        self.assertEqual(response.data['listing'], None)
        self.assertTrue('expires_date' in data)

    def test_create_agency_notification_app_mall_steward_invalid_format(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple agency test',
                'agency': {'invalid': 1}
                }
        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Valid Agency ID is required'])

    def test_create_agency_notification_app_mall_steward_invalid_id(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple agency test',
                'agency': {'id': -1}
                }
        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Could not find agency'])

    # TODO: test_create_agency_notification_org_steward (rivera 20160617)
    # TODO: test_create_agency_notification_org_steward_invalid (rivera 20160617)
    # TODO: test_create_agency_notification_user_unauthorized (rivera 20160617)

    def test_create_peer_notification_app_mall_steward(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {"expires_date": str(now),
                "message": "A Simple Peer to Peer Notification",
                "peer": {
                    "user": {
                      "username": "jones"
                    }}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'A Simple Peer to Peer Notification')
        self.assertEqual(response.data['notification_type'], 'peer')
        self.assertEqual(response.data['agency'], None)
        self.assertEqual(response.data['listing'], None)
        self.assertEqual(response.data['peer'], {'user': {'username': 'jones'}})
        self.assertTrue('expires_date' in data)

    @skip("should work when data script gets refactored (rivera 20160620)")
    def test_create_peer_bookmark_notification_app_mall_steward(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {"expires_date": str(now),
                "message": "A Simple Peer to Peer Notification",
                "peer": {
                    "user": {
                      "username": "jones"
                    },
                    "folder_name": "folder"}
                }
        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'A Simple Peer to Peer Notification')
        self.assertEqual(response.data['notification_type'], 'peer_bookmark')
        self.assertEqual(response.data['agency'], None)
        self.assertEqual(response.data['listing'], None)
        self.assertTrue('expires_date' in data)

    # TODO test_create_peer_notification_invalid (rivera 20160617)
    # TODO test_create_peer_bookmark_notification (rivera 20160617)

    def test_create_peer_bookmark_notification_integration(self):
        """
        test_create_peer_bookmark_notification_integration
        Listing ID: 1, 2, 3, 4
        wsmith (minitrue, stewarded_orgs: minitrue)
        julia (minitrue, stewarded_orgs: minitrue, miniluv)
        bigbrother2 - minitrue
        """
        response = _create_create_bookmark(self, 'wsmith', 3, folder_name='foldername1', status_code=201)
        self.assertEqual(response.data['listing']['id'], 3)

        response = _create_create_bookmark(self, 'wsmith', 4, folder_name='foldername1', status_code=201)
        self.assertEqual(response.data['listing']['id'], 4)

        # Compare Notifications for users
        usernames_list = {'bigbrother': ['listing-BreadBasketupdatenextweek',
                                         'listing-BreadBasketupdatenextweek',
                                         'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                         'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                 'jones': ['system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                           'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                 'julia': ['listing-Userhasratedlisting[LocationLister9]4stars',
                           'listing-Userhasratedlisting[LocationLister8]4stars',
                           'listing-Userhasratedlisting[LocationLister7]4stars',
                           'listing-Userhasratedlisting[LocationLister6]4stars',
                           'listing-Userhasratedlisting[LocationLister5]4stars',
                           'listing-Userhasratedlisting[LocationLister4]4stars',
                           'listing-Userhasratedlisting[LocationLister3]4stars',
                           'listing-Userhasratedlisting[LocationLister2]4stars',
                           'listing-Userhasratedlisting[LocationLister1]4stars',
                           'listing-Userhasratedlisting[LocationLister]4stars',
                           'listing-Userhasratedlisting[JotSpot9]4stars',
                           'listing-Userhasratedlisting[JotSpot8]4stars',
                           'listing-Userhasratedlisting[JotSpot7]4stars',
                           'listing-Userhasratedlisting[JotSpot6]4stars',
                           'listing-Userhasratedlisting[JotSpot5]4stars',
                           'listing-Userhasratedlisting[JotSpot4]4stars',
                           'listing-Userhasratedlisting[JotSpot3]4stars',
                           'listing-Userhasratedlisting[JotSpot2]4stars',
                           'listing-Userhasratedlisting[JotSpot1]4stars',
                           'listing-Userhasratedlisting[JotSpot]4stars',
                           'listing-Userhasratedlisting[ChartCourse9]5stars',
                           'listing-Userhasratedlisting[ChartCourse9]2stars',
                           'listing-Userhasratedlisting[ChartCourse8]5stars',
                           'listing-Userhasratedlisting[ChartCourse8]2stars',
                           'listing-Userhasratedlisting[ChartCourse7]5stars',
                           'listing-Userhasratedlisting[ChartCourse7]2stars',
                           'listing-Userhasratedlisting[ChartCourse6]5stars',
                           'listing-Userhasratedlisting[ChartCourse6]2stars',
                           'listing-Userhasratedlisting[ChartCourse5]5stars',
                           'listing-Userhasratedlisting[ChartCourse5]2stars',
                           'listing-Userhasratedlisting[ChartCourse4]5stars',
                           'listing-Userhasratedlisting[ChartCourse4]2stars',
                           'listing-Userhasratedlisting[ChartCourse3]5stars',
                           'listing-Userhasratedlisting[ChartCourse3]2stars',
                           'listing-Userhasratedlisting[ChartCourse2]5stars',
                           'listing-Userhasratedlisting[ChartCourse2]2stars',
                           'listing-Userhasratedlisting[ChartCourse1]5stars',
                           'listing-Userhasratedlisting[ChartCourse1]2stars',
                           'listing-Userhasratedlisting[ChartCourse]5stars',
                           'listing-Userhasratedlisting[ChartCourse]2stars',
                           'listing-Userhasratedlisting[BreadBasket9]5stars',
                           'listing-Userhasratedlisting[BreadBasket9]2stars',
                           'listing-Userhasratedlisting[BreadBasket8]5stars',
                           'listing-Userhasratedlisting[BreadBasket8]2stars',
                           'listing-Userhasratedlisting[BreadBasket7]5stars',
                           'listing-Userhasratedlisting[BreadBasket7]2stars',
                           'listing-Userhasratedlisting[BreadBasket6]5stars',
                           'listing-Userhasratedlisting[BreadBasket6]2stars',
                           'listing-Userhasratedlisting[BreadBasket5]5stars',
                           'listing-Userhasratedlisting[BreadBasket5]2stars',
                           'listing-Userhasratedlisting[BreadBasket4]5stars',
                           'listing-Userhasratedlisting[BreadBasket4]2stars',
                           'listing-Userhasratedlisting[BreadBasket3]5stars',
                           'listing-Userhasratedlisting[BreadBasket3]2stars',
                           'listing-Userhasratedlisting[BreadBasket2]5stars',
                           'listing-Userhasratedlisting[BreadBasket2]2stars',
                           'listing-Userhasratedlisting[BreadBasket1]5stars',
                           'listing-Userhasratedlisting[BreadBasket1]2stars',
                           'listing-Userhasratedlisting[BreadBasket]5stars',
                           'listing-Userhasratedlisting[BreadBasket]2stars',
                           'listing-Userhasratedlisting[AirMail9]1stars',
                           'listing-Userhasratedlisting[AirMail9]3stars',
                           'listing-Userhasratedlisting[AirMail9]5stars',
                           'listing-Userhasratedlisting[AirMail8]1stars',
                           'listing-Userhasratedlisting[AirMail8]3stars',
                           'listing-Userhasratedlisting[AirMail8]5stars',
                           'listing-Userhasratedlisting[AirMail7]1stars',
                           'listing-Userhasratedlisting[AirMail7]3stars',
                           'listing-Userhasratedlisting[AirMail7]5stars',
                           'listing-Userhasratedlisting[AirMail6]1stars',
                           'listing-Userhasratedlisting[AirMail6]3stars',
                           'listing-Userhasratedlisting[AirMail6]5stars',
                           'listing-Userhasratedlisting[AirMail5]1stars',
                           'listing-Userhasratedlisting[AirMail5]3stars',
                           'listing-Userhasratedlisting[AirMail5]5stars',
                           'listing-Userhasratedlisting[AirMail4]1stars',
                           'listing-Userhasratedlisting[AirMail4]3stars',
                           'listing-Userhasratedlisting[AirMail4]5stars',
                           'listing-Userhasratedlisting[AirMail3]1stars',
                           'listing-Userhasratedlisting[AirMail3]3stars',
                           'listing-Userhasratedlisting[AirMail3]5stars',
                           'listing-Userhasratedlisting[AirMail2]1stars',
                           'listing-Userhasratedlisting[AirMail2]3stars',
                           'listing-Userhasratedlisting[AirMail2]5stars',
                           'listing-Userhasratedlisting[AirMail1]1stars',
                           'listing-Userhasratedlisting[AirMail1]3stars',
                           'listing-Userhasratedlisting[AirMail1]5stars',
                           'listing-Userhasratedlisting[AirMail]1stars',
                           'listing-Userhasratedlisting[AirMail]3stars',
                           'listing-Userhasratedlisting[AirMail]5stars',
                           'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                           'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                 'wsmith': ['listing-BreadBasketupdatenextweek',
                            'listing-Skybox1updatenextweek',
                            'listing-AirMailupdatenextweek',
                            'listing-Skybox3updatenextweek',
                            'listing-Skybox2updatenextweek',
                            'listing-Skybox1updatenextweek',
                            'listing-AirMailupdatenextweek',
                            'listing-BreadBasketupdatenextweek',
                            'listing-Userhasratedlisting[LocationLister9]4stars',
                            'listing-Userhasratedlisting[LocationLister8]4stars',
                            'listing-Userhasratedlisting[LocationLister7]4stars',
                            'listing-Userhasratedlisting[LocationLister6]4stars',
                            'listing-Userhasratedlisting[LocationLister5]4stars',
                            'listing-Userhasratedlisting[LocationLister4]4stars',
                            'listing-Userhasratedlisting[LocationLister3]4stars',
                            'listing-Userhasratedlisting[LocationLister2]4stars',
                            'listing-Userhasratedlisting[LocationLister1]4stars',
                            'listing-Userhasratedlisting[LocationLister]4stars',
                            'listing-Userhasratedlisting[JotSpot9]4stars',
                            'listing-Userhasratedlisting[JotSpot8]4stars',
                            'listing-Userhasratedlisting[JotSpot7]4stars',
                            'listing-Userhasratedlisting[JotSpot6]4stars',
                            'listing-Userhasratedlisting[JotSpot5]4stars',
                            'listing-Userhasratedlisting[JotSpot4]4stars',
                            'listing-Userhasratedlisting[JotSpot3]4stars',
                            'listing-Userhasratedlisting[JotSpot2]4stars',
                            'listing-Userhasratedlisting[JotSpot1]4stars',
                            'listing-Userhasratedlisting[JotSpot]4stars',
                            'listing-Userhasratedlisting[ChartCourse9]5stars',
                            'listing-Userhasratedlisting[ChartCourse9]2stars',
                            'listing-Userhasratedlisting[ChartCourse8]5stars',
                            'listing-Userhasratedlisting[ChartCourse8]2stars',
                            'listing-Userhasratedlisting[ChartCourse7]5stars',
                            'listing-Userhasratedlisting[ChartCourse7]2stars',
                            'listing-Userhasratedlisting[ChartCourse6]5stars',
                            'listing-Userhasratedlisting[ChartCourse6]2stars',
                            'listing-Userhasratedlisting[ChartCourse5]5stars',
                            'listing-Userhasratedlisting[ChartCourse5]2stars',
                            'listing-Userhasratedlisting[ChartCourse4]5stars',
                            'listing-Userhasratedlisting[ChartCourse4]2stars',
                            'listing-Userhasratedlisting[ChartCourse3]5stars',
                            'listing-Userhasratedlisting[ChartCourse3]2stars',
                            'listing-Userhasratedlisting[ChartCourse2]5stars',
                            'listing-Userhasratedlisting[ChartCourse2]2stars',
                            'listing-Userhasratedlisting[ChartCourse1]5stars',
                            'listing-Userhasratedlisting[ChartCourse1]2stars',
                            'listing-Userhasratedlisting[ChartCourse]5stars',
                            'listing-Userhasratedlisting[ChartCourse]2stars',
                            'listing-Userhasratedlisting[BreadBasket9]5stars',
                            'listing-Userhasratedlisting[BreadBasket9]2stars',
                            'listing-Userhasratedlisting[BreadBasket8]5stars',
                            'listing-Userhasratedlisting[BreadBasket8]2stars',
                            'listing-Userhasratedlisting[BreadBasket7]5stars',
                            'listing-Userhasratedlisting[BreadBasket7]2stars',
                            'listing-Userhasratedlisting[BreadBasket6]5stars',
                            'listing-Userhasratedlisting[BreadBasket6]2stars',
                            'listing-Userhasratedlisting[BreadBasket5]5stars',
                            'listing-Userhasratedlisting[BreadBasket5]2stars',
                            'listing-Userhasratedlisting[BreadBasket4]5stars',
                            'listing-Userhasratedlisting[BreadBasket4]2stars',
                            'listing-Userhasratedlisting[BreadBasket3]5stars',
                            'listing-Userhasratedlisting[BreadBasket3]2stars',
                            'listing-Userhasratedlisting[BreadBasket2]5stars',
                            'listing-Userhasratedlisting[BreadBasket2]2stars',
                            'listing-Userhasratedlisting[BreadBasket1]5stars',
                            'listing-Userhasratedlisting[BreadBasket1]2stars',
                            'listing-Userhasratedlisting[BreadBasket]5stars',
                            'listing-Userhasratedlisting[BreadBasket]2stars',
                            'listing-Userhasratedlisting[AirMail9]1stars',
                            'listing-Userhasratedlisting[AirMail9]3stars',
                            'listing-Userhasratedlisting[AirMail9]5stars',
                            'listing-Userhasratedlisting[AirMail8]1stars',
                            'listing-Userhasratedlisting[AirMail8]3stars',
                            'listing-Userhasratedlisting[AirMail8]5stars',
                            'listing-Userhasratedlisting[AirMail7]1stars',
                            'listing-Userhasratedlisting[AirMail7]3stars',
                            'listing-Userhasratedlisting[AirMail7]5stars',
                            'listing-Userhasratedlisting[AirMail6]1stars',
                            'listing-Userhasratedlisting[AirMail6]3stars',
                            'listing-Userhasratedlisting[AirMail6]5stars',
                            'listing-Userhasratedlisting[AirMail5]1stars',
                            'listing-Userhasratedlisting[AirMail5]3stars',
                            'listing-Userhasratedlisting[AirMail5]5stars',
                            'listing-Userhasratedlisting[AirMail4]1stars',
                            'listing-Userhasratedlisting[AirMail4]3stars',
                            'listing-Userhasratedlisting[AirMail4]5stars',
                            'listing-Userhasratedlisting[AirMail3]1stars',
                            'listing-Userhasratedlisting[AirMail3]3stars',
                            'listing-Userhasratedlisting[AirMail3]5stars',
                            'listing-Userhasratedlisting[AirMail2]1stars',
                            'listing-Userhasratedlisting[AirMail2]3stars',
                            'listing-Userhasratedlisting[AirMail2]5stars',
                            'listing-Userhasratedlisting[AirMail1]1stars',
                            'listing-Userhasratedlisting[AirMail1]3stars',
                            'listing-Userhasratedlisting[AirMail1]5stars',
                            'listing-Userhasratedlisting[AirMail]1stars',
                            'listing-Userhasratedlisting[AirMail]3stars',
                            'listing-Userhasratedlisting[AirMail]5stars',
                            'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                            'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']}
        usernames_list_main = usernames_list
        usernames_list_actual = {}
        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/notification/'
            response = self.client.get(url, format='json')

            before_notification_ids = ['{}-{}'.format(entry.get('notification_type'), ''.join(entry.get('message').split())) for entry in response.data]
            usernames_list_actual[username] = before_notification_ids

        for username, ids_list in usernames_list.items():
            before_notification_ids = usernames_list_actual[username]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(ids_list, before_notification_ids, 'Checking for {}'.format(username))

        # Compare Library for users
        usernames_list = {'wsmith': ['Bread Basket-None',
                                     'Air Mail-None',
                                     'Skybox 1-None',
                                     'Skybox 2-None',
                                     'Skybox 3-None',
                                     'Air Mail 2-foldername1',
                                     'Air Mail 3-foldername1'],
                          'julia': [],
                          'jones': [],
                          'bigbrother': ['Bread Basket-None']}

        usernames_list_actual = {}
        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/library/'
            response = self.client.get(url, format='json')
            before_notification_ids = ['{}-{}'.format(entry['listing']['title'], entry['folder']) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            usernames_list_actual[username] = before_notification_ids

        for username, ids_list in usernames_list.items():
            before_notification_ids = usernames_list_actual[username]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(ids_list, before_notification_ids, 'Checking for {}'.format(username))

        # Create Bookmark
        response = _create_create_bookmark(self, 'bigbrother', 4, folder_name='foldername2', status_code=201)
        self.assertEqual(response.data['listing']['id'], 4)

        # Compare Library for users
        usernames_list = {'wsmith': ['Bread Basket-None',
                                     'Air Mail-None',
                                     'Skybox 1-None',
                                     'Skybox 2-None',
                                     'Skybox 3-None',
                                     'Air Mail 2-foldername1',
                                     'Air Mail 3-foldername1'],
                          'julia': [],
                          'jones': [],
                          'bigbrother': ['Bread Basket-None', 'Air Mail 3-foldername2']}

        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/library/'
            response = self.client.get(url, format='json')

            before_notification_ids = ['{}-{}'.format(entry['listing']['title'], entry['folder']) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(before_notification_ids, ids_list, 'Comparing Library for {}'.format(username))

        # Create Bookmark Notification
        bookmark_notification_ids = []
        bookmark_notification_ids_raw = []

        for i in range(3):
            user = generic_model_access.get_profile('wsmith').user
            self.client.force_authenticate(user=user)

            now = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=5)
            data = {'expires_date': str(now),
                    'message': 'A Simple Peer to Peer Notification',
                    'peer': {
                        'user': {
                          'username': 'julia',
                        },
                        'folder_name': 'foldername1'
                }}

            url = '/api/notification/'
            response = self.client.post(url, data, format='json')

            peer_data = {'user': {'username': 'julia'}, 'folder_name': 'foldername1'}  # '_bookmark_listing_ids': [3, 4]}
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['message'], 'A Simple Peer to Peer Notification')
            self.assertEqual(response.data['notification_type'], 'peer_bookmark')
            self.assertEqual(response.data['agency'], None)
            self.assertEqual(response.data['listing'], None)
            self.assertEqual(response.data['peer'], peer_data)
            self.assertTrue('expires_date' in data)

            bookmark_notification_ids.append('{}-{}'.format(response.data['notification_type'], ''.join(response.data['message'].split())))
            bookmark_notification_ids_raw.append(response.data['id'])

            # Compare Notifications for users
            usernames_list = copy.deepcopy(usernames_list_main)
            usernames_list['julia'] = bookmark_notification_ids[::-1] + usernames_list_main['julia']

            usernames_list_actual = {}
            for username, ids_list in usernames_list.items():
                user = generic_model_access.get_profile(username).user
                self.client.force_authenticate(user=user)

                url = '/api/self/notification/'
                response = self.client.get(url, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                before_notification_ids = ['{}-{}'.format(entry.get('notification_type'), ''.join(entry.get('message').split())) for entry in response.data]
                usernames_list_actual[username] = before_notification_ids

            for username, ids_list in usernames_list.items():
                before_notification_ids = usernames_list_actual[username]
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(ids_list, before_notification_ids, 'Checking for {}'.format(username))

        bookmark_notification1_id = bookmark_notification_ids_raw[0]

        # Import Bookmarks
        _import_bookmarks(self, 'julia', bookmark_notification1_id, status_code=201)

        # Compare Library for users
        usernames_list = {'wsmith': ['Bread Basket-None',
                                     'Air Mail-None',
                                     'Skybox 1-None',
                                     'Skybox 2-None',
                                     'Skybox 3-None',
                                     'Air Mail 2-foldername1',
                                     'Air Mail 3-foldername1'],
                          'julia': ['Air Mail 2-foldername1', 'Air Mail 3-foldername1'],
                          'jones': [],
                          'bigbrother': ['Bread Basket-None', 'Air Mail 3-foldername2']}

        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/library/'
            response = self.client.get(url, format='json')

            before_notification_ids = ['{}-{}'.format(entry['listing']['title'], entry['folder']) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(before_notification_ids, ids_list, 'Comparing Library for {}'.format(username))

        # Compare Notifications for users
        usernames_list = copy.deepcopy(usernames_list_main)
        usernames_list['julia'] = bookmark_notification_ids[::-1] + usernames_list_main['julia']

        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/notification/'
            response = self.client.get(url, format='json')

            before_notification_ids = ['{}-{}'.format(entry.get('notification_type'), ''.join(entry.get('message').split())) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(ids_list, before_notification_ids, 'Comparing Notifications for {}'.format(username))

    def test_delete_system_notification_apps_mall_steward(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/notification/1/'
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # TODO below test should work when permission gets refactored (rivera 20160620)
    @skip("should work when permission gets refactored (rivera 20160620)")
    def test_delete_system_notification_org_steward(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/notification/1/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_system_notification_user_unauthorized(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        url = '/api/notification/1/'
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO: Unittest for below
    # AMLNG-378 - As a user, I want to receive notification about changes on Listings I've bookmarked
    # AMLNG-377 - As an owner or ORG CS, I want to receive notification of user rating and reviews
    # AMLNG-376 - As a ORG CS, I want to receive notification of Listings submitted for my organization
    # AMLNG-173 - As Org Content Steward, I want notification if an owner has cancelled an app that was pending deletion
    # AMLNG-170 - As an Owner I want to receive notice of whether my deletion request has been approved or rejected
    # AMLNG-461 - As Developer, I want to refactor code to make it modular and easier way to add Notification Types
