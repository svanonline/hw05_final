from django.conf import settings
from django.core.paginator import Paginator


def get_page_context(request, queryset):
    paginator = Paginator(queryset, settings.POST_LENGTH)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }
