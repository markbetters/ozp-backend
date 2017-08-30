"""
pagination classes
https://github.com/encode/django-rest-framework/blob/master/rest_framework/pagination.py
"""
from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class StandardPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ReviewLimitOffsetPagination(pagination.LimitOffsetPagination):
    """
    Limit Offset Pagination for Reviews
    """

    def paginate_queryset(self, queryset, request, view=None):
        self.count_reviews = queryset.filter(review_parent__isnull=True).count()
        self.count_review_responses = queryset.filter(review_parent__isnull=False).count()
        return super(ReviewLimitOffsetPagination, self).paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('count_reviews', self.count_reviews),
            ('count_review_responses', self.count_review_responses),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
