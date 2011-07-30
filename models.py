from django.db import models
from datetime import datetime
from django.contrib import admin
from django.utils.translation import ugettext as _




class StringSetField(models.CommaSeparatedIntegerField):
    """A field that holds a set of strings.
    Subclass of CommaSeparatedIntegerField since the internal storage is the same.
    """

    description = "A field that holds a set of strings"

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        # from a db value to a python object
        if isinstance(value, (list, set, tuple)):
            return list(value)
        elif isinstance(value, basestring):
            return value.split(',')
        elif value is None:
            return []
        else:
            raise TypeError("StringSetField.to_python got an invalid type!")

    def get_prep_value(self, value):
        # from a python object to a db value
        if isinstance(value, (list, set, tuple)):
            return ','.join(value)
        elif isinstance(value, basestring):
            return value
        elif value is None:
            return None
        else:
            raise TypeError("StringSetField.get_prep_value got an invalid type!")


class NzbField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        # from a db value to a python object
        if isinstance(value, (list, set, tuple)):
            return list(value)
        elif isinstance(value, basestring):
            return value.split(',')
        elif value is None:
            return []
        else:
            raise TypeError("NzbField.to_python got an invalid type!")

    def get_prep_value(self, value):
        # from a python object to a db value
        if isinstance(value, (list, set, tuple)):
            return ','.join(value)
        elif isinstance(value, basestring):
            return value
        elif value is None:
            return None
        else:
            raise TypeError("NzbField.get_prep_value got an invalid type!")



class CategoryField(models.CharField):
    def __init__(self, *args, **kwargs):
        return __init__(self, max_length=30, *args, choices=(
            ('',''),
        ), **kwargs)

class SubCategoryField(StringSetField):
    def __init__(self, *args, **kwargs):
        return __init__(self, max_length=80, *args, choices=(
            ('',''),
        ), **kwargs)

    



#
# DATABASE INDEX FIELDS:
# 
# * id : primary key
# * spotid : unique
# * messageid : unique
# * timestamp : ordering (not unique)
#

class SpotnetPost(models.Model):
    # id # omesium db id

    # SPOTNET PARAMETERS
    spotid = models.PositiveIntegerField(editable=False, null=False) # spotnet post id
    messageid = models.CharField(max_length=80, editable=False, null=False) # spotnet message id ???
    poster = models.CharField(max_length=120, null=True)
    title = models.CharField(max_length=150, null=True)
    description = models.TextField(null=True)
    tag = models.CharField(max_length=100, null=True)
    timestamp = models.PositiveIntegerField(null=True, db_index=True)
    category = models.CharField(max_length=3, null=True, choices=(
        ('01', _('Image')),
        ('02', _('Sound')),
        ('03', _('Game')),
        ('04', _('Application')),
    ))
    subcategory = StringSetField(max_length=250, editable=False, null=True) ###
    image = models.CharField(max_length=250, null=True) ###
    website = models.CharField(max_length=150, null=True) ###
    size = models.BigIntegerField(max_length=33, null=True)
    nzb = NzbField(max_length=250, editable=False, null=True)

    # OMESIUM PARAMETERS
    state = models.SmallIntegerField(choices=(
        (0, _('Spotted')),
        (1, _('Queued')),
        (2, _('Downloading')),
        (3, _('Downloaded')),
    ), editable=False, default=0)


    class Meta:
        db_table = 'spotnet_post'
        unique_together = (('messageid',),('spotid',),)

    @models.permalink
    def get_absolute_url(self):
        return ('spotnet:viewpost', (), dict(id=self.id))


    def _datetime_get(self):
        return datetime.utcfromtimestamp(self.timestamp)
    def _datetime_set(self, dt):
        if isinstance(dt, (int,long,float)):
            self.timestamp = datetime
        elif isinstance(dt, datetime):
            self.timestamp = float(dt.strftime('%s'))
        else:
            raise TypeError
    datetime = property(_datetime_get, _datetime_set)

    @property
    def has_nzb(self):
        return len(self.nzb) > 0

    @property
    def description_markup(self):
        return self.description.replace('[br]','\n')



    @classmethod
    def from_spot(cls, spot):
        return cls(
            spotid = spot.id,
            messageid = spot.message_id[0:80],
            poster = spot.poster[0:120],
            title = spot.title[0:150],
            description = spot.description,
            tag = spot.tag[0:100] if spot.tag else None,
            timestamp = spot.timestamp,
            category = spot.category,
            subcategory = spot.subcategory[0:250],
            image = spot.image[0:250],
            website = spot.website[0:150] if spot.website else None,
            size = spot.size,
            nzb = spot.nzb[0:250],
        )

    def download(self, save_db=True):
        with open(os.path.join(download_nzb_folder,spotnet_post_to_filename(self)), 'w') as f:
            f.write(self.get_nzb_content())
            self.state = 1
            if save_db:
                self.save()

    def get_nzb_file(self):
        pass

    def get_nzb_content(self):
        # connet to server
        news_server = get_news_server(0)
        nzb_fetcher = pySpotnet.NZBFetcher(n)
        # create spot
        spot = pySpotnet.Spot(self.postid, self.messageid)
        spot.nzb = self.nzb
        # return nzb content
        return nzb.get(spot)





class SpotnetPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'poster', 'tag', 'category', 'datetime')
    list_filter = ('category',)
    ordering = ('-timestamp',)
    #search_fields = ['title','description','tag']   # disabled since it's way to slow

    inlines = []
    actions = []


admin.site.register(SpotnetPost, SpotnetPostAdmin)

