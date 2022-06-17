from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    date_str = timezone.now().year

    return {
        'year': date_str
    }
