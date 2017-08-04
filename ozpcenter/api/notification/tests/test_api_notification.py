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
            self.assertIn('notification_id', current_notification)
            self.assertIn('read_status', current_notification)
            self.assertIn('acknowledged_status', current_notification)

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
                         '90-listing-Auserhasratedlisting<b>LocationLister9</b>4stars',
                         '89-listing-Auserhasratedlisting<b>LocationLister8</b>4stars',
                         '88-listing-Auserhasratedlisting<b>LocationLister7</b>4stars',
                         '87-listing-Auserhasratedlisting<b>LocationLister6</b>4stars',
                         '86-listing-Auserhasratedlisting<b>LocationLister5</b>4stars',
                         '85-listing-Auserhasratedlisting<b>LocationLister4</b>4stars',
                         '84-listing-Auserhasratedlisting<b>LocationLister3</b>4stars',
                         '83-listing-Auserhasratedlisting<b>LocationLister2</b>4stars',
                         '82-listing-Auserhasratedlisting<b>LocationLister1</b>4stars',
                         '81-listing-Auserhasratedlisting<b>LocationLister</b>4stars',
                         '80-listing-Auserhasratedlisting<b>JotSpot9</b>4stars',
                         '79-listing-Auserhasratedlisting<b>JotSpot8</b>4stars',
                         '78-listing-Auserhasratedlisting<b>JotSpot7</b>4stars',
                         '77-listing-Auserhasratedlisting<b>JotSpot6</b>4stars',
                         '76-listing-Auserhasratedlisting<b>JotSpot5</b>4stars',
                         '75-listing-Auserhasratedlisting<b>JotSpot4</b>4stars',
                         '74-listing-Auserhasratedlisting<b>JotSpot3</b>4stars',
                         '73-listing-Auserhasratedlisting<b>JotSpot2</b>4stars',
                         '72-listing-Auserhasratedlisting<b>JotSpot1</b>4stars',
                         '71-listing-Auserhasratedlisting<b>JotSpot</b>4stars',
                         '30-listing-Auserhasratedlisting<b>ChartCourse9</b>5stars',
                         '30-listing-Auserhasratedlisting<b>ChartCourse9</b>2stars',
                         '29-listing-Auserhasratedlisting<b>ChartCourse8</b>5stars',
                         '29-listing-Auserhasratedlisting<b>ChartCourse8</b>2stars',
                         '28-listing-Auserhasratedlisting<b>ChartCourse7</b>5stars',
                         '28-listing-Auserhasratedlisting<b>ChartCourse7</b>2stars',
                         '27-listing-Auserhasratedlisting<b>ChartCourse6</b>5stars',
                         '27-listing-Auserhasratedlisting<b>ChartCourse6</b>2stars',
                         '26-listing-Auserhasratedlisting<b>ChartCourse5</b>5stars',
                         '26-listing-Auserhasratedlisting<b>ChartCourse5</b>2stars',
                         '25-listing-Auserhasratedlisting<b>ChartCourse4</b>5stars',
                         '25-listing-Auserhasratedlisting<b>ChartCourse4</b>2stars',
                         '24-listing-Auserhasratedlisting<b>ChartCourse3</b>5stars',
                         '24-listing-Auserhasratedlisting<b>ChartCourse3</b>2stars',
                         '23-listing-Auserhasratedlisting<b>ChartCourse2</b>5stars',
                         '23-listing-Auserhasratedlisting<b>ChartCourse2</b>2stars',
                         '22-listing-Auserhasratedlisting<b>ChartCourse1</b>5stars',
                         '22-listing-Auserhasratedlisting<b>ChartCourse1</b>2stars',
                         '21-listing-Auserhasratedlisting<b>ChartCourse</b>5stars',
                         '21-listing-Auserhasratedlisting<b>ChartCourse</b>2stars',
                         '20-listing-Auserhasratedlisting<b>BreadBasket9</b>5stars',
                         '20-listing-Auserhasratedlisting<b>BreadBasket9</b>2stars',
                         '19-listing-Auserhasratedlisting<b>BreadBasket8</b>5stars',
                         '19-listing-Auserhasratedlisting<b>BreadBasket8</b>2stars',
                         '18-listing-Auserhasratedlisting<b>BreadBasket7</b>5stars',
                         '18-listing-Auserhasratedlisting<b>BreadBasket7</b>2stars',
                         '17-listing-Auserhasratedlisting<b>BreadBasket6</b>5stars',
                         '17-listing-Auserhasratedlisting<b>BreadBasket6</b>2stars',
                         '16-listing-Auserhasratedlisting<b>BreadBasket5</b>5stars',
                         '16-listing-Auserhasratedlisting<b>BreadBasket5</b>2stars',
                         '15-listing-Auserhasratedlisting<b>BreadBasket4</b>5stars',
                         '15-listing-Auserhasratedlisting<b>BreadBasket4</b>2stars',
                         '14-listing-Auserhasratedlisting<b>BreadBasket3</b>5stars',
                         '14-listing-Auserhasratedlisting<b>BreadBasket3</b>2stars',
                         '13-listing-Auserhasratedlisting<b>BreadBasket2</b>5stars',
                         '13-listing-Auserhasratedlisting<b>BreadBasket2</b>2stars',
                         '12-listing-Auserhasratedlisting<b>BreadBasket1</b>5stars',
                         '12-listing-Auserhasratedlisting<b>BreadBasket1</b>2stars',
                         '11-listing-Auserhasratedlisting<b>BreadBasket</b>5stars',
                         '11-listing-Auserhasratedlisting<b>BreadBasket</b>2stars',
                         '10-listing-Auserhasratedlisting<b>AirMail9</b>1star',
                         '10-listing-Auserhasratedlisting<b>AirMail9</b>3stars',
                         '10-listing-Auserhasratedlisting<b>AirMail9</b>5stars',
                         '9-listing-Auserhasratedlisting<b>AirMail8</b>1star',
                         '9-listing-Auserhasratedlisting<b>AirMail8</b>3stars',
                         '9-listing-Auserhasratedlisting<b>AirMail8</b>5stars',
                         '8-listing-Auserhasratedlisting<b>AirMail7</b>1star',
                         '8-listing-Auserhasratedlisting<b>AirMail7</b>3stars',
                         '8-listing-Auserhasratedlisting<b>AirMail7</b>5stars',
                         '7-listing-Auserhasratedlisting<b>AirMail6</b>1star',
                         '7-listing-Auserhasratedlisting<b>AirMail6</b>3stars',
                         '7-listing-Auserhasratedlisting<b>AirMail6</b>5stars',
                         '6-listing-Auserhasratedlisting<b>AirMail5</b>1star',
                         '6-listing-Auserhasratedlisting<b>AirMail5</b>3stars',
                         '6-listing-Auserhasratedlisting<b>AirMail5</b>5stars',
                         '5-listing-Auserhasratedlisting<b>AirMail4</b>1star',
                         '5-listing-Auserhasratedlisting<b>AirMail4</b>3stars',
                         '5-listing-Auserhasratedlisting<b>AirMail4</b>5stars',
                         '4-listing-Auserhasratedlisting<b>AirMail3</b>1star',
                         '4-listing-Auserhasratedlisting<b>AirMail3</b>3stars',
                         '4-listing-Auserhasratedlisting<b>AirMail3</b>5stars',
                         '3-listing-Auserhasratedlisting<b>AirMail2</b>1star',
                         '3-listing-Auserhasratedlisting<b>AirMail2</b>3stars',
                         '3-listing-Auserhasratedlisting<b>AirMail2</b>5stars',
                         '2-listing-Auserhasratedlisting<b>AirMail1</b>1star',
                         '2-listing-Auserhasratedlisting<b>AirMail1</b>3stars',
                         '2-listing-Auserhasratedlisting<b>AirMail1</b>5stars',
                         '1-listing-Auserhasratedlisting<b>AirMail</b>1star',
                         '1-listing-Auserhasratedlisting<b>AirMail</b>3stars',
                         '1-listing-Auserhasratedlisting<b>AirMail</b>5stars',
                         'None-system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                         'None-system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']

        self.assertListEqual(notification_list, expected_data)

        # Get reversed order
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/?ordering=-notification__created_date'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification_list = ['{}-{}-{}'.format(entry['entity_id'], entry['notification_type'], ''.join(entry['message'].split())) for entry in response.data]

        self.assertEqual(notification_list, expected_data)

        # Get ascending order
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/?ordering=notification__created_date'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification_list = ['{}-{}-{}'.format(entry['entity_id'], entry['notification_type'], ''.join(entry['message'].split())) for entry in response.data]
        self.assertEqual(notification_list, list(reversed(expected_data)))

    def test_dismiss_self_notification(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        mailbox_ids = []
        notification_ids = []
        for i in response.data:
            notification_ids.append([i['notification_id'], ''.join(i['message'].split())])
            mailbox_ids.append(i['id'])

        expected = [[106, 'BreadBasketupdatenextweek'],
                    [105, 'Skybox1updatenextweek'],
                    [103, 'AirMailupdatenextweek'],
                    [99, 'Skybox3updatenextweek'],
                    [98, 'Skybox2updatenextweek'],
                    [97, 'Skybox1updatenextweek'],
                    [96, 'AirMailupdatenextweek'],
                    [95, 'BreadBasketupdatenextweek'],
                    [94, 'Auserhasratedlisting<b>LocationLister9</b>4stars'],
                    [93, 'Auserhasratedlisting<b>LocationLister8</b>4stars'],
                    [92, 'Auserhasratedlisting<b>LocationLister7</b>4stars'],
                    [91, 'Auserhasratedlisting<b>LocationLister6</b>4stars'],
                    [90, 'Auserhasratedlisting<b>LocationLister5</b>4stars'],
                    [89, 'Auserhasratedlisting<b>LocationLister4</b>4stars'],
                    [88, 'Auserhasratedlisting<b>LocationLister3</b>4stars'],
                    [87, 'Auserhasratedlisting<b>LocationLister2</b>4stars'],
                    [86, 'Auserhasratedlisting<b>LocationLister1</b>4stars'],
                    [85, 'Auserhasratedlisting<b>LocationLister</b>4stars'],
                    [84, 'Auserhasratedlisting<b>JotSpot9</b>4stars'],
                    [83, 'Auserhasratedlisting<b>JotSpot8</b>4stars'],
                    [82, 'Auserhasratedlisting<b>JotSpot7</b>4stars'],
                    [81, 'Auserhasratedlisting<b>JotSpot6</b>4stars'],
                    [80, 'Auserhasratedlisting<b>JotSpot5</b>4stars'],
                    [79, 'Auserhasratedlisting<b>JotSpot4</b>4stars'],
                    [78, 'Auserhasratedlisting<b>JotSpot3</b>4stars'],
                    [77, 'Auserhasratedlisting<b>JotSpot2</b>4stars'],
                    [76, 'Auserhasratedlisting<b>JotSpot1</b>4stars'],
                    [75, 'Auserhasratedlisting<b>JotSpot</b>4stars'],
                    [74, 'Auserhasratedlisting<b>ChartCourse9</b>5stars'],
                    [73, 'Auserhasratedlisting<b>ChartCourse9</b>2stars'],
                    [72, 'Auserhasratedlisting<b>ChartCourse8</b>5stars'],
                    [71, 'Auserhasratedlisting<b>ChartCourse8</b>2stars'],
                    [70, 'Auserhasratedlisting<b>ChartCourse7</b>5stars'],
                    [69, 'Auserhasratedlisting<b>ChartCourse7</b>2stars'],
                    [68, 'Auserhasratedlisting<b>ChartCourse6</b>5stars'],
                    [67, 'Auserhasratedlisting<b>ChartCourse6</b>2stars'],
                    [66, 'Auserhasratedlisting<b>ChartCourse5</b>5stars'],
                    [65, 'Auserhasratedlisting<b>ChartCourse5</b>2stars'],
                    [64, 'Auserhasratedlisting<b>ChartCourse4</b>5stars'],
                    [63, 'Auserhasratedlisting<b>ChartCourse4</b>2stars'],
                    [62, 'Auserhasratedlisting<b>ChartCourse3</b>5stars'],
                    [61, 'Auserhasratedlisting<b>ChartCourse3</b>2stars'],
                    [60, 'Auserhasratedlisting<b>ChartCourse2</b>5stars'],
                    [59, 'Auserhasratedlisting<b>ChartCourse2</b>2stars'],
                    [58, 'Auserhasratedlisting<b>ChartCourse1</b>5stars'],
                    [57, 'Auserhasratedlisting<b>ChartCourse1</b>2stars'],
                    [56, 'Auserhasratedlisting<b>ChartCourse</b>5stars'],
                    [55, 'Auserhasratedlisting<b>ChartCourse</b>2stars'],
                    [54, 'Auserhasratedlisting<b>BreadBasket9</b>5stars'],
                    [53, 'Auserhasratedlisting<b>BreadBasket9</b>2stars'],
                    [52, 'Auserhasratedlisting<b>BreadBasket8</b>5stars'],
                    [51, 'Auserhasratedlisting<b>BreadBasket8</b>2stars'],
                    [50, 'Auserhasratedlisting<b>BreadBasket7</b>5stars'],
                    [49, 'Auserhasratedlisting<b>BreadBasket7</b>2stars'],
                    [48, 'Auserhasratedlisting<b>BreadBasket6</b>5stars'],
                    [47, 'Auserhasratedlisting<b>BreadBasket6</b>2stars'],
                    [46, 'Auserhasratedlisting<b>BreadBasket5</b>5stars'],
                    [45, 'Auserhasratedlisting<b>BreadBasket5</b>2stars'],
                    [44, 'Auserhasratedlisting<b>BreadBasket4</b>5stars'],
                    [43, 'Auserhasratedlisting<b>BreadBasket4</b>2stars'],
                    [42, 'Auserhasratedlisting<b>BreadBasket3</b>5stars'],
                    [41, 'Auserhasratedlisting<b>BreadBasket3</b>2stars'],
                    [40, 'Auserhasratedlisting<b>BreadBasket2</b>5stars'],
                    [39, 'Auserhasratedlisting<b>BreadBasket2</b>2stars'],
                    [38, 'Auserhasratedlisting<b>BreadBasket1</b>5stars'],
                    [37, 'Auserhasratedlisting<b>BreadBasket1</b>2stars'],
                    [36, 'Auserhasratedlisting<b>BreadBasket</b>5stars'],
                    [35, 'Auserhasratedlisting<b>BreadBasket</b>2stars'],
                    [34, 'Auserhasratedlisting<b>AirMail9</b>1star'],
                    [33, 'Auserhasratedlisting<b>AirMail9</b>3stars'],
                    [32, 'Auserhasratedlisting<b>AirMail9</b>5stars'],
                    [31, 'Auserhasratedlisting<b>AirMail8</b>1star'],
                    [30, 'Auserhasratedlisting<b>AirMail8</b>3stars'],
                    [29, 'Auserhasratedlisting<b>AirMail8</b>5stars'],
                    [28, 'Auserhasratedlisting<b>AirMail7</b>1star'],
                    [27, 'Auserhasratedlisting<b>AirMail7</b>3stars'],
                    [26, 'Auserhasratedlisting<b>AirMail7</b>5stars'],
                    [25, 'Auserhasratedlisting<b>AirMail6</b>1star'],
                    [24, 'Auserhasratedlisting<b>AirMail6</b>3stars'],
                    [23, 'Auserhasratedlisting<b>AirMail6</b>5stars'],
                    [22, 'Auserhasratedlisting<b>AirMail5</b>1star'],
                    [21, 'Auserhasratedlisting<b>AirMail5</b>3stars'],
                    [20, 'Auserhasratedlisting<b>AirMail5</b>5stars'],
                    [19, 'Auserhasratedlisting<b>AirMail4</b>1star'],
                    [18, 'Auserhasratedlisting<b>AirMail4</b>3stars'],
                    [17, 'Auserhasratedlisting<b>AirMail4</b>5stars'],
                    [16, 'Auserhasratedlisting<b>AirMail3</b>1star'],
                    [15, 'Auserhasratedlisting<b>AirMail3</b>3stars'],
                    [14, 'Auserhasratedlisting<b>AirMail3</b>5stars'],
                    [13, 'Auserhasratedlisting<b>AirMail2</b>1star'],
                    [12, 'Auserhasratedlisting<b>AirMail2</b>3stars'],
                    [11, 'Auserhasratedlisting<b>AirMail2</b>5stars'],
                    [10, 'Auserhasratedlisting<b>AirMail1</b>1star'],
                    [9, 'Auserhasratedlisting<b>AirMail1</b>3stars'],
                    [8, 'Auserhasratedlisting<b>AirMail1</b>5stars'],
                    [7, 'Auserhasratedlisting<b>AirMail</b>1star'],
                    [6, 'Auserhasratedlisting<b>AirMail</b>3stars'],
                    [5, 'Auserhasratedlisting<b>AirMail</b>5stars'],
                    [2, 'Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B'],
                    [1, 'Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']]

        self.assertEqual(expected, notification_ids)

        # now dismiss the first notification
        dismissed_mailbox_id = mailbox_ids[0]
        url = url + str(dismissed_mailbox_id) + '/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # now get our notifications again, make sure the one was removed
        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append([i['notification_id'], ''.join(i['message'].split())])

        expected = [[105, 'Skybox1updatenextweek'],
                    [103, 'AirMailupdatenextweek'],
                    [99, 'Skybox3updatenextweek'],
                    [98, 'Skybox2updatenextweek'],
                    [97, 'Skybox1updatenextweek'],
                    [96, 'AirMailupdatenextweek'],
                    [95, 'BreadBasketupdatenextweek'],
                    [94, 'Auserhasratedlisting<b>LocationLister9</b>4stars'],
                    [93, 'Auserhasratedlisting<b>LocationLister8</b>4stars'],
                    [92, 'Auserhasratedlisting<b>LocationLister7</b>4stars'],
                    [91, 'Auserhasratedlisting<b>LocationLister6</b>4stars'],
                    [90, 'Auserhasratedlisting<b>LocationLister5</b>4stars'],
                    [89, 'Auserhasratedlisting<b>LocationLister4</b>4stars'],
                    [88, 'Auserhasratedlisting<b>LocationLister3</b>4stars'],
                    [87, 'Auserhasratedlisting<b>LocationLister2</b>4stars'],
                    [86, 'Auserhasratedlisting<b>LocationLister1</b>4stars'],
                    [85, 'Auserhasratedlisting<b>LocationLister</b>4stars'],
                    [84, 'Auserhasratedlisting<b>JotSpot9</b>4stars'],
                    [83, 'Auserhasratedlisting<b>JotSpot8</b>4stars'],
                    [82, 'Auserhasratedlisting<b>JotSpot7</b>4stars'],
                    [81, 'Auserhasratedlisting<b>JotSpot6</b>4stars'],
                    [80, 'Auserhasratedlisting<b>JotSpot5</b>4stars'],
                    [79, 'Auserhasratedlisting<b>JotSpot4</b>4stars'],
                    [78, 'Auserhasratedlisting<b>JotSpot3</b>4stars'],
                    [77, 'Auserhasratedlisting<b>JotSpot2</b>4stars'],
                    [76, 'Auserhasratedlisting<b>JotSpot1</b>4stars'],
                    [75, 'Auserhasratedlisting<b>JotSpot</b>4stars'],
                    [74, 'Auserhasratedlisting<b>ChartCourse9</b>5stars'],
                    [73, 'Auserhasratedlisting<b>ChartCourse9</b>2stars'],
                    [72, 'Auserhasratedlisting<b>ChartCourse8</b>5stars'],
                    [71, 'Auserhasratedlisting<b>ChartCourse8</b>2stars'],
                    [70, 'Auserhasratedlisting<b>ChartCourse7</b>5stars'],
                    [69, 'Auserhasratedlisting<b>ChartCourse7</b>2stars'],
                    [68, 'Auserhasratedlisting<b>ChartCourse6</b>5stars'],
                    [67, 'Auserhasratedlisting<b>ChartCourse6</b>2stars'],
                    [66, 'Auserhasratedlisting<b>ChartCourse5</b>5stars'],
                    [65, 'Auserhasratedlisting<b>ChartCourse5</b>2stars'],
                    [64, 'Auserhasratedlisting<b>ChartCourse4</b>5stars'],
                    [63, 'Auserhasratedlisting<b>ChartCourse4</b>2stars'],
                    [62, 'Auserhasratedlisting<b>ChartCourse3</b>5stars'],
                    [61, 'Auserhasratedlisting<b>ChartCourse3</b>2stars'],
                    [60, 'Auserhasratedlisting<b>ChartCourse2</b>5stars'],
                    [59, 'Auserhasratedlisting<b>ChartCourse2</b>2stars'],
                    [58, 'Auserhasratedlisting<b>ChartCourse1</b>5stars'],
                    [57, 'Auserhasratedlisting<b>ChartCourse1</b>2stars'],
                    [56, 'Auserhasratedlisting<b>ChartCourse</b>5stars'],
                    [55, 'Auserhasratedlisting<b>ChartCourse</b>2stars'],
                    [54, 'Auserhasratedlisting<b>BreadBasket9</b>5stars'],
                    [53, 'Auserhasratedlisting<b>BreadBasket9</b>2stars'],
                    [52, 'Auserhasratedlisting<b>BreadBasket8</b>5stars'],
                    [51, 'Auserhasratedlisting<b>BreadBasket8</b>2stars'],
                    [50, 'Auserhasratedlisting<b>BreadBasket7</b>5stars'],
                    [49, 'Auserhasratedlisting<b>BreadBasket7</b>2stars'],
                    [48, 'Auserhasratedlisting<b>BreadBasket6</b>5stars'],
                    [47, 'Auserhasratedlisting<b>BreadBasket6</b>2stars'],
                    [46, 'Auserhasratedlisting<b>BreadBasket5</b>5stars'],
                    [45, 'Auserhasratedlisting<b>BreadBasket5</b>2stars'],
                    [44, 'Auserhasratedlisting<b>BreadBasket4</b>5stars'],
                    [43, 'Auserhasratedlisting<b>BreadBasket4</b>2stars'],
                    [42, 'Auserhasratedlisting<b>BreadBasket3</b>5stars'],
                    [41, 'Auserhasratedlisting<b>BreadBasket3</b>2stars'],
                    [40, 'Auserhasratedlisting<b>BreadBasket2</b>5stars'],
                    [39, 'Auserhasratedlisting<b>BreadBasket2</b>2stars'],
                    [38, 'Auserhasratedlisting<b>BreadBasket1</b>5stars'],
                    [37, 'Auserhasratedlisting<b>BreadBasket1</b>2stars'],
                    [36, 'Auserhasratedlisting<b>BreadBasket</b>5stars'],
                    [35, 'Auserhasratedlisting<b>BreadBasket</b>2stars'],
                    [34, 'Auserhasratedlisting<b>AirMail9</b>1star'],
                    [33, 'Auserhasratedlisting<b>AirMail9</b>3stars'],
                    [32, 'Auserhasratedlisting<b>AirMail9</b>5stars'],
                    [31, 'Auserhasratedlisting<b>AirMail8</b>1star'],
                    [30, 'Auserhasratedlisting<b>AirMail8</b>3stars'],
                    [29, 'Auserhasratedlisting<b>AirMail8</b>5stars'],
                    [28, 'Auserhasratedlisting<b>AirMail7</b>1star'],
                    [27, 'Auserhasratedlisting<b>AirMail7</b>3stars'],
                    [26, 'Auserhasratedlisting<b>AirMail7</b>5stars'],
                    [25, 'Auserhasratedlisting<b>AirMail6</b>1star'],
                    [24, 'Auserhasratedlisting<b>AirMail6</b>3stars'],
                    [23, 'Auserhasratedlisting<b>AirMail6</b>5stars'],
                    [22, 'Auserhasratedlisting<b>AirMail5</b>1star'],
                    [21, 'Auserhasratedlisting<b>AirMail5</b>3stars'],
                    [20, 'Auserhasratedlisting<b>AirMail5</b>5stars'],
                    [19, 'Auserhasratedlisting<b>AirMail4</b>1star'],
                    [18, 'Auserhasratedlisting<b>AirMail4</b>3stars'],
                    [17, 'Auserhasratedlisting<b>AirMail4</b>5stars'],
                    [16, 'Auserhasratedlisting<b>AirMail3</b>1star'],
                    [15, 'Auserhasratedlisting<b>AirMail3</b>3stars'],
                    [14, 'Auserhasratedlisting<b>AirMail3</b>5stars'],
                    [13, 'Auserhasratedlisting<b>AirMail2</b>1star'],
                    [12, 'Auserhasratedlisting<b>AirMail2</b>3stars'],
                    [11, 'Auserhasratedlisting<b>AirMail2</b>5stars'],
                    [10, 'Auserhasratedlisting<b>AirMail1</b>1star'],
                    [9, 'Auserhasratedlisting<b>AirMail1</b>3stars'],
                    [8, 'Auserhasratedlisting<b>AirMail1</b>5stars'],
                    [7, 'Auserhasratedlisting<b>AirMail</b>1star'],
                    [6, 'Auserhasratedlisting<b>AirMail</b>3stars'],
                    [5, 'Auserhasratedlisting<b>AirMail</b>5stars'],
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
        expected = ['1-listing-AirMailupdatenextweek',
                    '1-listing-AirMailupdatenextweek',
                    '1-listing-Auserhasratedlisting<b>AirMail</b>1star',
                    '1-listing-Auserhasratedlisting<b>AirMail</b>3stars',
                    '1-listing-Auserhasratedlisting<b>AirMail</b>5stars']

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
                 'julia': ['listing-Auserhasratedlisting<b>LocationLister9</b>4stars',
                           'listing-Auserhasratedlisting<b>LocationLister8</b>4stars',
                           'listing-Auserhasratedlisting<b>LocationLister7</b>4stars',
                           'listing-Auserhasratedlisting<b>LocationLister6</b>4stars',
                           'listing-Auserhasratedlisting<b>LocationLister5</b>4stars',
                           'listing-Auserhasratedlisting<b>LocationLister4</b>4stars',
                           'listing-Auserhasratedlisting<b>LocationLister3</b>4stars',
                           'listing-Auserhasratedlisting<b>LocationLister2</b>4stars',
                           'listing-Auserhasratedlisting<b>LocationLister1</b>4stars',
                           'listing-Auserhasratedlisting<b>LocationLister</b>4stars',
                           'listing-Auserhasratedlisting<b>JotSpot9</b>4stars',
                           'listing-Auserhasratedlisting<b>JotSpot8</b>4stars',
                           'listing-Auserhasratedlisting<b>JotSpot7</b>4stars',
                           'listing-Auserhasratedlisting<b>JotSpot6</b>4stars',
                           'listing-Auserhasratedlisting<b>JotSpot5</b>4stars',
                           'listing-Auserhasratedlisting<b>JotSpot4</b>4stars',
                           'listing-Auserhasratedlisting<b>JotSpot3</b>4stars',
                           'listing-Auserhasratedlisting<b>JotSpot2</b>4stars',
                           'listing-Auserhasratedlisting<b>JotSpot1</b>4stars',
                           'listing-Auserhasratedlisting<b>JotSpot</b>4stars',
                           'listing-Auserhasratedlisting<b>ChartCourse9</b>5stars',
                           'listing-Auserhasratedlisting<b>ChartCourse9</b>2stars',
                           'listing-Auserhasratedlisting<b>ChartCourse8</b>5stars',
                           'listing-Auserhasratedlisting<b>ChartCourse8</b>2stars',
                           'listing-Auserhasratedlisting<b>ChartCourse7</b>5stars',
                           'listing-Auserhasratedlisting<b>ChartCourse7</b>2stars',
                           'listing-Auserhasratedlisting<b>ChartCourse6</b>5stars',
                           'listing-Auserhasratedlisting<b>ChartCourse6</b>2stars',
                           'listing-Auserhasratedlisting<b>ChartCourse5</b>5stars',
                           'listing-Auserhasratedlisting<b>ChartCourse5</b>2stars',
                           'listing-Auserhasratedlisting<b>ChartCourse4</b>5stars',
                           'listing-Auserhasratedlisting<b>ChartCourse4</b>2stars',
                           'listing-Auserhasratedlisting<b>ChartCourse3</b>5stars',
                           'listing-Auserhasratedlisting<b>ChartCourse3</b>2stars',
                           'listing-Auserhasratedlisting<b>ChartCourse2</b>5stars',
                           'listing-Auserhasratedlisting<b>ChartCourse2</b>2stars',
                           'listing-Auserhasratedlisting<b>ChartCourse1</b>5stars',
                           'listing-Auserhasratedlisting<b>ChartCourse1</b>2stars',
                           'listing-Auserhasratedlisting<b>ChartCourse</b>5stars',
                           'listing-Auserhasratedlisting<b>ChartCourse</b>2stars',
                           'listing-Auserhasratedlisting<b>BreadBasket9</b>5stars',
                           'listing-Auserhasratedlisting<b>BreadBasket9</b>2stars',
                           'listing-Auserhasratedlisting<b>BreadBasket8</b>5stars',
                           'listing-Auserhasratedlisting<b>BreadBasket8</b>2stars',
                           'listing-Auserhasratedlisting<b>BreadBasket7</b>5stars',
                           'listing-Auserhasratedlisting<b>BreadBasket7</b>2stars',
                           'listing-Auserhasratedlisting<b>BreadBasket6</b>5stars',
                           'listing-Auserhasratedlisting<b>BreadBasket6</b>2stars',
                           'listing-Auserhasratedlisting<b>BreadBasket5</b>5stars',
                           'listing-Auserhasratedlisting<b>BreadBasket5</b>2stars',
                           'listing-Auserhasratedlisting<b>BreadBasket4</b>5stars',
                           'listing-Auserhasratedlisting<b>BreadBasket4</b>2stars',
                           'listing-Auserhasratedlisting<b>BreadBasket3</b>5stars',
                           'listing-Auserhasratedlisting<b>BreadBasket3</b>2stars',
                           'listing-Auserhasratedlisting<b>BreadBasket2</b>5stars',
                           'listing-Auserhasratedlisting<b>BreadBasket2</b>2stars',
                           'listing-Auserhasratedlisting<b>BreadBasket1</b>5stars',
                           'listing-Auserhasratedlisting<b>BreadBasket1</b>2stars',
                           'listing-Auserhasratedlisting<b>BreadBasket</b>5stars',
                           'listing-Auserhasratedlisting<b>BreadBasket</b>2stars',
                           'listing-Auserhasratedlisting<b>AirMail9</b>1star',
                           'listing-Auserhasratedlisting<b>AirMail9</b>3stars',
                           'listing-Auserhasratedlisting<b>AirMail9</b>5stars',
                           'listing-Auserhasratedlisting<b>AirMail8</b>1star',
                           'listing-Auserhasratedlisting<b>AirMail8</b>3stars',
                           'listing-Auserhasratedlisting<b>AirMail8</b>5stars',
                           'listing-Auserhasratedlisting<b>AirMail7</b>1star',
                           'listing-Auserhasratedlisting<b>AirMail7</b>3stars',
                           'listing-Auserhasratedlisting<b>AirMail7</b>5stars',
                           'listing-Auserhasratedlisting<b>AirMail6</b>1star',
                           'listing-Auserhasratedlisting<b>AirMail6</b>3stars',
                           'listing-Auserhasratedlisting<b>AirMail6</b>5stars',
                           'listing-Auserhasratedlisting<b>AirMail5</b>1star',
                           'listing-Auserhasratedlisting<b>AirMail5</b>3stars',
                           'listing-Auserhasratedlisting<b>AirMail5</b>5stars',
                           'listing-Auserhasratedlisting<b>AirMail4</b>1star',
                           'listing-Auserhasratedlisting<b>AirMail4</b>3stars',
                           'listing-Auserhasratedlisting<b>AirMail4</b>5stars',
                           'listing-Auserhasratedlisting<b>AirMail3</b>1star',
                           'listing-Auserhasratedlisting<b>AirMail3</b>3stars',
                           'listing-Auserhasratedlisting<b>AirMail3</b>5stars',
                           'listing-Auserhasratedlisting<b>AirMail2</b>1star',
                           'listing-Auserhasratedlisting<b>AirMail2</b>3stars',
                           'listing-Auserhasratedlisting<b>AirMail2</b>5stars',
                           'listing-Auserhasratedlisting<b>AirMail1</b>1star',
                           'listing-Auserhasratedlisting<b>AirMail1</b>3stars',
                           'listing-Auserhasratedlisting<b>AirMail1</b>5stars',
                           'listing-Auserhasratedlisting<b>AirMail</b>1star',
                           'listing-Auserhasratedlisting<b>AirMail</b>3stars',
                           'listing-Auserhasratedlisting<b>AirMail</b>5stars',
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
                            'listing-Auserhasratedlisting<b>LocationLister9</b>4stars',
                            'listing-Auserhasratedlisting<b>LocationLister8</b>4stars',
                            'listing-Auserhasratedlisting<b>LocationLister7</b>4stars',
                            'listing-Auserhasratedlisting<b>LocationLister6</b>4stars',
                            'listing-Auserhasratedlisting<b>LocationLister5</b>4stars',
                            'listing-Auserhasratedlisting<b>LocationLister4</b>4stars',
                            'listing-Auserhasratedlisting<b>LocationLister3</b>4stars',
                            'listing-Auserhasratedlisting<b>LocationLister2</b>4stars',
                            'listing-Auserhasratedlisting<b>LocationLister1</b>4stars',
                            'listing-Auserhasratedlisting<b>LocationLister</b>4stars',
                            'listing-Auserhasratedlisting<b>JotSpot9</b>4stars',
                            'listing-Auserhasratedlisting<b>JotSpot8</b>4stars',
                            'listing-Auserhasratedlisting<b>JotSpot7</b>4stars',
                            'listing-Auserhasratedlisting<b>JotSpot6</b>4stars',
                            'listing-Auserhasratedlisting<b>JotSpot5</b>4stars',
                            'listing-Auserhasratedlisting<b>JotSpot4</b>4stars',
                            'listing-Auserhasratedlisting<b>JotSpot3</b>4stars',
                            'listing-Auserhasratedlisting<b>JotSpot2</b>4stars',
                            'listing-Auserhasratedlisting<b>JotSpot1</b>4stars',
                            'listing-Auserhasratedlisting<b>JotSpot</b>4stars',
                            'listing-Auserhasratedlisting<b>ChartCourse9</b>5stars',
                            'listing-Auserhasratedlisting<b>ChartCourse9</b>2stars',
                            'listing-Auserhasratedlisting<b>ChartCourse8</b>5stars',
                            'listing-Auserhasratedlisting<b>ChartCourse8</b>2stars',
                            'listing-Auserhasratedlisting<b>ChartCourse7</b>5stars',
                            'listing-Auserhasratedlisting<b>ChartCourse7</b>2stars',
                            'listing-Auserhasratedlisting<b>ChartCourse6</b>5stars',
                            'listing-Auserhasratedlisting<b>ChartCourse6</b>2stars',
                            'listing-Auserhasratedlisting<b>ChartCourse5</b>5stars',
                            'listing-Auserhasratedlisting<b>ChartCourse5</b>2stars',
                            'listing-Auserhasratedlisting<b>ChartCourse4</b>5stars',
                            'listing-Auserhasratedlisting<b>ChartCourse4</b>2stars',
                            'listing-Auserhasratedlisting<b>ChartCourse3</b>5stars',
                            'listing-Auserhasratedlisting<b>ChartCourse3</b>2stars',
                            'listing-Auserhasratedlisting<b>ChartCourse2</b>5stars',
                            'listing-Auserhasratedlisting<b>ChartCourse2</b>2stars',
                            'listing-Auserhasratedlisting<b>ChartCourse1</b>5stars',
                            'listing-Auserhasratedlisting<b>ChartCourse1</b>2stars',
                            'listing-Auserhasratedlisting<b>ChartCourse</b>5stars',
                            'listing-Auserhasratedlisting<b>ChartCourse</b>2stars',
                            'listing-Auserhasratedlisting<b>BreadBasket9</b>5stars',
                            'listing-Auserhasratedlisting<b>BreadBasket9</b>2stars',
                            'listing-Auserhasratedlisting<b>BreadBasket8</b>5stars',
                            'listing-Auserhasratedlisting<b>BreadBasket8</b>2stars',
                            'listing-Auserhasratedlisting<b>BreadBasket7</b>5stars',
                            'listing-Auserhasratedlisting<b>BreadBasket7</b>2stars',
                            'listing-Auserhasratedlisting<b>BreadBasket6</b>5stars',
                            'listing-Auserhasratedlisting<b>BreadBasket6</b>2stars',
                            'listing-Auserhasratedlisting<b>BreadBasket5</b>5stars',
                            'listing-Auserhasratedlisting<b>BreadBasket5</b>2stars',
                            'listing-Auserhasratedlisting<b>BreadBasket4</b>5stars',
                            'listing-Auserhasratedlisting<b>BreadBasket4</b>2stars',
                            'listing-Auserhasratedlisting<b>BreadBasket3</b>5stars',
                            'listing-Auserhasratedlisting<b>BreadBasket3</b>2stars',
                            'listing-Auserhasratedlisting<b>BreadBasket2</b>5stars',
                            'listing-Auserhasratedlisting<b>BreadBasket2</b>2stars',
                            'listing-Auserhasratedlisting<b>BreadBasket1</b>5stars',
                            'listing-Auserhasratedlisting<b>BreadBasket1</b>2stars',
                            'listing-Auserhasratedlisting<b>BreadBasket</b>5stars',
                            'listing-Auserhasratedlisting<b>BreadBasket</b>2stars',
                            'listing-Auserhasratedlisting<b>AirMail9</b>1star',
                            'listing-Auserhasratedlisting<b>AirMail9</b>3stars',
                            'listing-Auserhasratedlisting<b>AirMail9</b>5stars',
                            'listing-Auserhasratedlisting<b>AirMail8</b>1star',
                            'listing-Auserhasratedlisting<b>AirMail8</b>3stars',
                            'listing-Auserhasratedlisting<b>AirMail8</b>5stars',
                            'listing-Auserhasratedlisting<b>AirMail7</b>1star',
                            'listing-Auserhasratedlisting<b>AirMail7</b>3stars',
                            'listing-Auserhasratedlisting<b>AirMail7</b>5stars',
                            'listing-Auserhasratedlisting<b>AirMail6</b>1star',
                            'listing-Auserhasratedlisting<b>AirMail6</b>3stars',
                            'listing-Auserhasratedlisting<b>AirMail6</b>5stars',
                            'listing-Auserhasratedlisting<b>AirMail5</b>1star',
                            'listing-Auserhasratedlisting<b>AirMail5</b>3stars',
                            'listing-Auserhasratedlisting<b>AirMail5</b>5stars',
                            'listing-Auserhasratedlisting<b>AirMail4</b>1star',
                            'listing-Auserhasratedlisting<b>AirMail4</b>3stars',
                            'listing-Auserhasratedlisting<b>AirMail4</b>5stars',
                            'listing-Auserhasratedlisting<b>AirMail3</b>1star',
                            'listing-Auserhasratedlisting<b>AirMail3</b>3stars',
                            'listing-Auserhasratedlisting<b>AirMail3</b>5stars',
                            'listing-Auserhasratedlisting<b>AirMail2</b>1star',
                            'listing-Auserhasratedlisting<b>AirMail2</b>3stars',
                            'listing-Auserhasratedlisting<b>AirMail2</b>5stars',
                            'listing-Auserhasratedlisting<b>AirMail1</b>1star',
                            'listing-Auserhasratedlisting<b>AirMail1</b>3stars',
                            'listing-Auserhasratedlisting<b>AirMail1</b>5stars',
                            'listing-Auserhasratedlisting<b>AirMail</b>1star',
                            'listing-Auserhasratedlisting<b>AirMail</b>3stars',
                            'listing-Auserhasratedlisting<b>AirMail</b>5stars',
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
