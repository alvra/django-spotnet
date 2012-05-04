from django.utils.translation import ugettext as _
from django.shortcuts import render


def index(request):
    return render(
        request,
        'index.html', 
        {},
    )
