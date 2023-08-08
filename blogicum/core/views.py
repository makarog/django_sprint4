from django.shortcuts import render


def e_handler404(request, exception):
    """
    Обработка ошибки 404
    """
    return render(request, 'core/404.html', status=404)


def csrf_failure(request, reason=''):
    """
    Обработка ошибки 403
    """
    return render(request, 'pages/403csrf.html', status=403)


def e_handler500(request):
    """
    Обработка ошибки 500
    """
    return render(request, 'pages/500.html', status=500)
