from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination, _positive_int


class MainPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 50
    choices = [2, 5, 7, 9, 10, 15, 20, 25, 30, 50]
    page_size = 7

    def get_page_size(self, request):
        if self.page_size_query_param:
            choices = self.choices
            page_size = request.query_params.get(self.page_size_query_param)
            if not page_size:
                return self.page_size
            else:
                if int(page_size) in choices:
                    return int(page_size)
                else:
                    return self.page_size