import json
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseNotFound, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.functional import wraps  # TODO: use this for decorators
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import settings
from models import Post, PostDownloaded
from downloading import DownloadError, PostDownload
from selector import QuerySelector
from actions import DeleteAction, DownloadNzbAction, DownloadRelatedNzbAction
from searcher import Searcher
from subcategories import Subcategory


try:
    from django.shortcuts import render
except ImportError:
    # for django==1.2 compatibility
    from django.shortcuts import render_to_response
    from django.template import RequestContext

    def render(request, template, context):
        return render_to_response(
            template,
            context,
            context_instance=RequestContext(request),
        )


def authenticate_base(user):
    if settings.ANONYMOUS_ACTION != 'allow' and user.is_anonymous():
        if settings.ANONYMOUS_ACTION == '403':
            return HttpResponseForbidden()
        elif settings.ANONYMOUS_ACTION == 'login':
            # TODO: which one to use here?
            #from django.conf.settings import LOGIN_URL
            #return HttpResponseRedirect(LOGIN_URL)
            return HttpResponseRedirect(reverse('login'))
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


def get_paginate_template():
    if settings.POSTS_PAGINATE_FULL:
        return 'spotnet/paginate_full.html'
    else:
        return 'spotnet/paginate.html'


@authenticate
def search(request, search=None, cats=None, scats=None):
    page_number = request.GET.get('page', 1)
    searcher = Searcher(search, cats, scats)
    snps = Post.objects.order_by('-posted')
    snps = searcher.filter_queryset(snps)
    searcher.unfilter_categories()

    selector = QuerySelector(snps, dict(
        download=DownloadNzbAction(),
    ))

    if request.method == 'POST':
        action_response = selector.apply_action(request)
        if isinstance(action_response, HttpResponse):
            return action_response

    paginator = Paginator(
        selector,
        settings.POST_PER_PAGE,
        allow_empty_first_page=True,
        orphans=0,
    )

    if page_number == "last":
        page = paginator.page(paginator.num_pages)
    else:
        try:
            page = paginator.page(page_number)
        except InvalidPage, EmptyPage:
            raise Http404
    return render(
        request,
        'spotnet/list.html',
        dict(
            searcher=searcher,
            page=page,
            paginate_template=get_paginate_template(),
            navigator_template="spotnet/paginate.html",  # TODO: use settings here
        ),
    )


@authenticate
def viewpost(request, id):
    post = get_object_or_404(Post, id=id)
    return render(
        request,
        'spotnet/viewpost.html',
        dict(
            post=post,
            download=PostDownload(post),
        ),
    )


@authenticate
def download(request, id, dls=None):
    post = get_object_or_404(Post, id=id)
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
        if request.user.is_authenticated():
            post.mark_downloaded(request.user)

    if request.is_ajax():
        if isinstance(e, DownloadError):
            return HttpResponse(json.dumps(dict(
                success=False,
                error=x.as_json_object(),
            )))
        else:
            obj = dict(
                success=True,
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
        download=DownloadRelatedNzbAction(),
    )
    actions.update(extra_actions)
    selector = QuerySelector(objects, actions)

    if request.method == 'POST':
        action_response = selector.apply_action(request)
        if isinstance(action_response, HttpResponse):
            return action_response

    paginator = Paginator(
        selector,
        settings.POST_PER_PAGE,
        allow_empty_first_page=True,
        orphans=settings.POST_LIST_ORPHANS,
    )
    try:
        page = paginator.page(page)
    except InvalidPage, EmptyPage:
        raise Http404
    return render(
        request,
        'spotnet/list_related.html',
        dict(
            title=title,
            page=page,
            paginate_template=get_paginate_template(),
        ),
    )


@authenticate
def downloaded(request):
    page = request.GET.get('page', 1)
    if request.user.is_anonymous():
        objects = PostDownloaded.objects.none()
        # TODO: is there something more sensible to do here?
    else:
        objects = PostDownloaded.objects.order_by('-created') \
            .select_related('post').filter(user=request.user)

    return view_related_post_list(
        request,
        objects,
        page,
        _('Downloaded'),
        dict(
            delete=DeleteAction(objects.model, title=_('Remove from list')),
        )
    )


@authenticate
def update(request):
    pass  # TODO


@authenticate
def download_nzb(request, id):
    pass  # TODO
