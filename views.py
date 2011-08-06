from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext as _
import json
from models import SpotnetPost, PostDownloaded, PostWatch, PostRecommendation
from downloading import DownloadError
from helpers import SpotDownload
import settings
#from paginator import Paginator, InvalidPage, EmptyPage
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from selector import QuerySelector
from actions import DeleteAction, DownloadNzbAction, DownloadRelatedNzbAction
from searcher import Searcher
from subcategories import Subcategory





def authenticate_base(user):
    if settings.ANONYMOUS_ACTION != 'allow' and user.is_anonymous():
        if settings.ANONYMOUS_ACTION == '403':
            return HttpResponseForbidden()
        else:
            return HttpResponseNotFound()
    else:
        return None

def authenticate(view):
    def _authenticated_view(request, *args, **kwargs):
        res = authenticate_base(request.user)
        if res:
            return res
        else:
            return view(request, *args, **kwargs)
    return _authenticated_view





@authenticate
def search(request, search=None, cats=None, scats=None):
    page = request.GET.get('page', 1)
    searcher = Searcher(search, cats, scats)
    snps = SpotnetPost.objects.order_by('-posted')
    snps = searcher.filter_queryset(snps)
    searcher.unfilter_categories()

    selector = QuerySelector(snps, dict(
       download = DownloadNzbAction(),
    ))

    if request.method == 'POST':
        action_response = selector.apply_action(request)
        if isinstance(action_response, HttpResponse):
            return action_response

    paginator = Paginator(selector, settings.POST_PER_PAGE, allow_empty_first_page=True, orphans=settings.POST_LIST_ORPHANS)
    try:
        page = paginator.page(page)
    except InvalidPage, EmptyPage:
        raise Http404
    return render_to_response(
        'django_spotnet/list.html',
        dict(
            searcher = searcher,
            page = page,
        ),
        context_instance = RequestContext(request)
    )



@authenticate
def viewpost(request, id):
    post = get_object_or_404(SpotnetPost, id=id)
    return render_to_response(
        'django_spotnet/viewpost.html',
        dict(
            post = post,
            download = SpotDownload(post),
        ),
        context_instance = RequestContext(request)
    )





@authenticate
def download(request, id, dls=None):
    post = get_object_or_404(SpotnetPost, id=id)
    if dls is None:
        server = settings.DOWNLOAD_SERVERS.get_default()
    else:
        server = settings.DOWNLOAD_SERVERS.get_server(dls)
    if server is None:
        raise Http404

    try:
        x = server.download_spot_base(request.user, post.identifier, post)
    except DownloadError as e:
        x = e
    else:
        post.mark_downloaded(request.user)

    if request.is_ajax():
        if isinstance(e, DownloadError):
            return HttpResponse(json.dumps(dict(
                success = False,
                error = x.as_json_object(),
            )))
        else:
            obj = dict(
                success = True,
            )
            if x is not None:
                obj['message'] = x
            return HttpResponse(json.dumps(obj))
    else:
        if isinstance(x, DownloadError):
            messages.error(request, x.as_message())
        else:
            messages.success(request, x)
        return HttpResponseRedirect(post.get_absolute_url())





def view_related_post_list(request, objects, page, title, extra_actions={}):
    actions = dict(
       download = DownloadRelatedNzbAction(),
    )
    actions.update(extra_actions)
    selector = QuerySelector(objects, actions)

    if request.method == 'POST':
        action_response = selector.apply_action(request)
        if isinstance(action_response, HttpResponse):
            return action_response

    paginator = Paginator(selector, settings.POST_PER_PAGE, allow_empty_first_page=True, orphans=settings.POST_LIST_ORPHANS)
    try:
        page = paginator.page(page)
    except InvalidPage, EmptyPage:
        raise Http404
    return render_to_response(
        'django_spotnet/list_related.html',
        dict(
            title = title,
            page = page,
        ),
        context_instance = RequestContext(request)
    )





@authenticate
def downloaded(request):
    page = request.GET.get('page', 1)
    objects = PostDownloaded.objects.order_by('-created').select_related('post').filter(user=request.user)

    return view_related_post_list(request, objects, page, _('Downloaded'), dict(
       delete = DeleteAction(objects.model, title=_('Remove from list')),
    ))
    



@authenticate
def watchlist(request):
    page = request.GET.get('page', 1)
    objects = PostWatch.objects.order_by('-created').select_related('post').filter(user=request.user)

    return view_related_post_list(request, objects, page, _('Watching'), dict(
       delete = DeleteAction(objects.model, title=_('Unwatch')),
    ))



@authenticate
def recommendations_made(request):
    page = request.GET.get('page', 1)
    objects = PostRecommendation.objects.order_by('-created').select_related('post').filter(from_user=request.user)

    return view_related_post_list(request, objects, page, _('Recommendations made'))



@authenticate
def recommendations(request):
    page = request.GET.get('page', 1)
    #objects = PostRecommendation.objects.order_by('-created').select_related('post').filter(to_users__contains=request.user)
    objects = request.user.spotnet_recommended_to.all()

    return view_related_post_list(request, objects, page, _('Recommended'))



@authenticate
def create_recommendation(request, id):
    pass # TODO





@authenticate
def update(request):
    pass





