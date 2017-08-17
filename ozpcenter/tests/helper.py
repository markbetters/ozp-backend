"""
Test Utility Helper

Function to help unit tests
"""
import os

import yaml

TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..','scripts', 'test_data')


class ListingFileClass(object):
    """
    Listing File

    from ozpcenter.tests.helper import ListingFile; ListingFile.filter_listings(is_enabled=True,approval_status='S')
    """

    def filter_listings(self, **kwargs):
        """
        filter_listings(hello='d',hel='da')
        kwargs = {'hello': 'd', 'hel': 'da'}

        kwargs order is not guaranteed
        """
        listings_data  = self.listing_records()

        listing_entries = []
        for current_listing_data in listings_data:
            current_listing = current_listing_data['listing']
            listing_activity = current_listing_data['listing_activity']

            current_listing['approval_status'] = listing_activity[-1]['action']

            accept_listing = True

            for keyword_key, keyword_value in kwargs.items():
                postfix = None
                if '__' in keyword_key:
                    keyword_key_split = keyword_key.split('__')
                    keyword_key = keyword_key_split[0]
                    postfix = keyword_key_split[1]

                # Check to see if keyword exist in lisiting
                if keyword_key in current_listing:
                    if postfix == 'in':
                        keyword_key_set = set(keyword_value)
                        current_listing_set = set(current_listing[keyword_key])
                        if len(current_listing_set.intersection(keyword_key_set)) == 0:
                            accept_listing = False
                    else:
                        if not current_listing[keyword_key] == keyword_value:
                            accept_listing = False

                else:
                    raise Exception('Keyword {} is not in the listing'.format(keyword_key))



            if accept_listing:
                listing_entries.append(current_listing)

        return listing_entries


    def __init__(self, listing_file_name=None):
        self.listing_file_path = os.path.join(TEST_DATA_PATH, listing_file_name or 'listings.yaml')

    def listing_records(self):
        """
        Extract Listing Records from listings.yaml
        """
        listings_data = None
        with open(self.listing_file_path, 'r') as stream:
            try:
                listings_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                raise
        return listings_data

    def listings_titles(self):
        """
        Extract Listing's titles from listing.yaml file

        Return a sorted list of titles
        """
        listings_data  = self.listing_records()
        return sorted([current_record['listing']['title'] for current_record in listings_data])

    def listings_filter_by_categories(self, categories=None):
        """
        Extract Listing's titles from listing.yaml file

        Hint: This does not deal with private apps

        Return a sorted list of listing
        """
        categories = set(categories) or set()
        listings_data  = self.listing_records()

        listing_entries = []

        for current_listing_data in listings_data:
            current_listing = current_listing_data['listing']
            current_listing_categories = set(current_listing['categories'])

            if current_listing_categories.intersection(categories):
                listing_entries.append(current_listing)

        return sorted(listing_entries, key=lambda entry: entry['title'])

    def listings_tags(self):
        """
        Extract Listing's tags from listing.yaml file

        Return a sorted list of tags
        """
        listings_data  = self.listing_records()

        library_entries = []
        listing_tags = set()
        for current_listing_data in listings_data:
            current_listing = current_listing_data['listing']

            for current_tag in current_listing['tags']:
                listing_tags.add(current_tag)
        return sorted(list(listing_tags))


ListingFile = ListingFileClass()
