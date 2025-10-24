from rest_framework.pagination import PageNumberPagination
from rest_framework.utils.urls import replace_query_param

class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that extends PageNumberPagination to include
    'first' and 'last' page links in the response.
    """

    def get_paginated_response(self, data):
        """
        Return a paginated style Response object with first and last links added.
        """
        response = super().get_paginated_response(data)
        response.data['first'] = self.get_first_link()
        response.data['last'] = self.get_last_link()
        return response

    def get_first_link(self):
        """
        Return the URL for the first page.
        """
        if self.page.paginator.num_pages <= 1:
            return None
        url = self.request.build_absolute_uri()
        return replace_query_param(url, self.page_query_param, 1)

    def get_last_link(self):
        """
        Return the URL for the last page.
        """
        if self.page.paginator.num_pages <= 1:
            return None
        url = self.request.build_absolute_uri()
        total_pages = self.page.paginator.num_pages
        return replace_query_param(url, self.page_query_param, total_pages)