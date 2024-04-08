from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 3
    # page_size_query_param = 'ps'
    # page_query_param = 'p'
    max_page_size = 10


class StandardResultsSetPagination(PageNumberPagination):
    # page_size = 6
    page_size = 16
    page_size_query_param = 'page_size'
    max_page_size = 20


class OffsetPagination(LimitOffsetPagination):
    default_limit = 3
    limit_query_param = 'l'
    offset_query_param = 'o'
    max_limit = 50
