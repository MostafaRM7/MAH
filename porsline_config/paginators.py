from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class MainPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 50
    choices = [2, 5, 7, 9, 10, 15, 20, 25, 30, 50]

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                choices = self.choices
                page_size = int(request.query_params.get(self.page_size_query_param, choices[2]))
                if page_size not in choices:
                    page_size = choices[2]
                return page_size
            except Exception as e:
                print(e)
                return choices[2]
