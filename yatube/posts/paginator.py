from django.core.paginator import Paginator


def pagination(request, post_list, posts_per_page):
    paginator = Paginator(post_list, posts_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
