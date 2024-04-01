from rest_framework.pagination import PageNumberPagination


class MainPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 50
    choices = [7, 25, 50, 100, 150]
    page_size = 7

    def get_page_size(self, request):
        if self.page_size_query_param:
            choices = self.choices
            page_size = request.query_params.get(self.page_size_query_param)

            if page_size is None:  # Check if page_size is not provided
                return self.page_size  # Return the default page size

            try:
                page_size = int(page_size)
                if page_size in choices:
                    return page_size
                else:
                    return self.page_size  # Return the default page size if the value is not in choices
            except ValueError:
                return self.page_size  # Return the default page size if page_size is not a valid integer

        return self.page_size
