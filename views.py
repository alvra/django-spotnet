from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import get_object_or_404

from models import SpotnetPost





PAGINATOR_OBJECTS_PER_PAGE = 50





def authenticate(user):
    if settings.SPOTNET_ANONYMOUS_ACTION != 'allow' and user.is_anonymous():
        if settings.SPOTNET_ANONYMOUS_ACTION == '403':
            return HttpResponseForbidden()   # TODO: make sure this turns into the default 404 page...
        else:
            return HttpResponseNotFound()   # TODO: make sure this turns into the default 403 page...
    else:
        return None
    




def index(request):
    res = authenticate(request.user)
    if res:
        return res
    # user is allowed
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        return HttpResponseNotFound()
    category = request.GET.get('cat', None)
    #if category and category exists:
    #    snps = SpotnetPost.objects.filter(category=category).order_by('-timestamp')
    #else
    snps = SpotnetPost.objects.order_by('-timestamp')
    paginator = Paginator(snps, PAGINATOR_OBJECTS_PER_PAGE)
    return render_to_response(
        'spotnet_index.html',
        dict(
            page = paginator.page(page),
        ),
        context_instance = RequestContext(request)
    )
    


def viewpost(request, id):
    res = authenticate(request.user)
    if res:
        return res
    # user is allowed
    post = get_object_or_404(SpotnetPost, id=id)
    return render_to_response(
        'spotnet_viewpost.html',
        dict(
            post = post,
        ),
        context_instance = RequestContext(request)
    )
    
    



