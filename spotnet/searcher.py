from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext
from django.http import Http404
import settings





class Searcher(object):
    def __init__(self, search=None, categories=None, subcategories=None):
        self.search = search or ''
        self.categories = categories.split(',') if categories else []
        self.subcategories = subcategories.split(',') if subcategories else []
        # clean attributes
        self.categories = [self.clean_category(cat) for cat in self.categories]
        self.categories = [cat for cat in self.categories if cat is not None]
        

    def clean_category(self, cat):
        if isinstance(cat, int):
            return cat
        else:
            try:
                return int(cat)
            except ValueError:
                c = settings.CATEGORY_REVERSED_MAPPING.get(cat, None)
                if c is None:
                    raise Http404
                else:
                    return c

    def clean_subcategory(self, cat):
        if isinstance(cat, int):
            return cat
        else:
            try:
                return int(cat)
            except ValueError:
                c = settings.CATEGORY_REVERSED_MAPPING.get(cat, None)
                if c is None:
                    raise Http404
                else:
                    return c

    def filter_queryset(self, qs):
        # filter search
        if self.search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(tag__icontains=search) |
                Q(description__icontains=search)
            )
        # filter categories
        if self.categories:
            qs = qs.filter(category__in = self.categories)
        # filter subcategories
        # TODO
        return qs

    def create_url(self, search, cats, scats):
        kwargs = {}
        if search:
            kwargs['search'] = search
        if cats:
            kwargs['cats'] = ','.join(settings.CATEGORY_MAPPING[c] for c in cats)
        if scats:
            kwargs['scats'] = ','.join(settings.SUBCATEGORY_MAPPING[c] for c in scats)
        return reverse('spotnet:search', **kwargs)
        

    # properties

    @property
    def is_category_filtered(self):
        return len(self.categories) > 0

    @property
    def is_subcategory_filtered(self):
        return len(self.subcategories) > 0

    # methods to create search urls

    def unfilter_categories(self):
        return self.create_url(self.search, [], self.subcategories)

    def single_category_filters(self):
        kwargs = {}
        if self.search:
            kwargs['search'] = self.search
        if self.subcategories:
            kwargs['scats'] = ','.join(settings.SUBCATEGORY_MAPPING[c] for c in self.subcategories)
        for catid, cat in settings.CATEGORY_MAPPING.iteritems():
            if len(self.categories) == 1 and catid in self.categories:
                yield None, ugettext(cat).capitalize()
            else:
                k = dict(
                    cats = cat,
                )
                k.update(kwargs)
                yield reverse('spotnet:search', kwargs=k), ugettext(cat).capitalize()

    def add_category_filters(self):
        kwargs = {}
        if self.search:
            kwargs['search'] = self.search
        if self.subcategories:
            kwargs['scats'] = ','.join(settings.SUBCATEGORY_MAPPING[c] for c in self.subcategories)
        for catid, cat in settings.CATEGORY_MAPPING.iteritems():
            if catid not in self.categories:
                k = dict(
                    cats = ','.join([settings.CATEGORY_MAPPING[c] for c in self.categories]+[cat]),
                )
                k.update(kwargs)
                yield reverse('spotnet:search', kwargs=k), ugettext(cat).capitalize()
            else:
                yield None, ugettext(cat).capitalize()

    def single_subcategory_filters(self):
        return [] # TODO



