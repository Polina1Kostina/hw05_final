import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    year_now = datetime.datetime.today().year
    return {
        'year': year_now
    }
