from django.db import models, IntegrityError
from cStringIO import StringIO
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from fields import StringSetField, NzbField, CategoryField, SubCategoryField
from subcategories import Subcategory





#
# ID's ON THE Post
#       and where they come from...
#
# * id : the id of the post in our database (used in this app for views etc.)
# * spotid : increasing number (differs per usenet server)
# * message_id : unique message id used by the NNTP protocol
#





#
# DATABASE INDEX FIELDS:
# 
# * id : primary key
# * spotid : not unique (over multiple usenet servers)
# * messageid : unique
# * posted : ordering (not unique)
#





class Post(models.Model):
    # id # omesium db id

    # SPOTNET PARAMETERS
    #postnumber = models.PositiveIntegerField(editable=False, null=False) # spotnet post id
    messageid = models.CharField(max_length=80, editable=False, null=False) # spotnet message id ???
    poster = models.CharField(max_length=120, null=True)
    title = models.CharField(max_length=150, null=True)
    description = models.TextField(null=True)
    tag = models.CharField(max_length=100, null=True)
    posted = models.DateTimeField(null=True, db_index=True)
    category = models.PositiveSmallIntegerField(null=True, choices=(
        (1, _('Image')),
        (2, _('Sound')),
        (3, _('Game')),
        (4, _('Application')),
    ))
    subcategory_codes = StringSetField(max_length=250, editable=False, null=True, db_column='subcategories') ###
    image = models.CharField(max_length=250, null=True) ###
    website = models.CharField(max_length=150, null=True) ###
    size = models.BigIntegerField(max_length=33, null=True)
    nzb = NzbField(max_length=250, editable=False, null=True)



    class Meta:
        db_table = 'spotnet_post'
        verbose_name = _('spotnet post')
        unique_together = (('messageid',),)

    @models.permalink
    def get_absolute_url(self):
        return ('spotnet:viewpost', (), dict(id=self.id))

    def mark_downloaded(self, user):
        if user.is_authenticated():
            try:
                PostDownloaded.objects.create(
                    user = user,
                    post = self,
                )
            except IntegrityError:
                pass

    # public properties that can be used to list
    # details about this spotnet post

    @property
    def has_nzb(self):
        return len(self.nzb) > 0

    @property
    def description_markup(self):
        return self.description.replace('[br]','\n')

    @property
    def subcategories(self):
        s = self.subcategory_codes
        return (Subcategory(code) for code in self.subcategory_codes)

    # this is the identifier that is passed to download servers
    # it is intended to be one-to-one with posts,
    # but also useful as title for the download on servers

    @property
    def identifier(self):
        return '%s: %s' % (self.pk, self.title)

    @classmethod
    def from_identifier(cls, identifier):
        id,title = identifier.split(': ', 1)
        try:
            return cls.objects.get(id=id) # , title=title)
        except cls.DoesNotExist:
            return None

    # methods for extracting the nzb file

    def get_nzb_file(self, connection=None):
        return StringIO(self.get_nzb_content(connection))

    def get_nzb_content(self, connection=None):
        if not connection:
            # create a new connection and close it again
            from connection import Connection
            connection = Connection(connect=True)
            nzb = connection.get_nzb(self)
            connection.disconnect()
            return nzb
        else:
            # leave the connection open
            return connection.get_nzb(self)

    # internal methods

    @classmethod
    def from_raw(cls, raw):
        return cls(
            #postnumber = raw.postnumber,
            messageid = raw.messageid[0:80],
            poster = raw.poster,
            title = raw.subject[0:150],
            description = raw.description,
            tag = raw.tag[0:100] if raw.tag else None,
            posted = raw.posted,
            category = raw.category if raw.category else None,
            # limit the number of subcategories,
            # some people give posts way too many subcategories
            # with an length of 5 joined with comma's
            # this gives an difference of 1 with the maximum lenght
            subcategory_codes = raw.subcategories[0:Post._meta.get_field('subcategory_codes').max_length//6],
            image = raw.image[0:250] if raw.image else None,
            website = raw.website[0:150] if raw.website else None,
            size = raw.size if raw.size else None,
            nzb = raw.nzb,
        )



class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'poster', 'tag', 'category', 'posted')
    list_filter = ('category',)
    ordering = ('-posted',)
    #search_fields = ['title','description','tag']   # disabled since it's way to slow

    inlines = []
    actions = []

admin.site.register(Post, PostAdmin)







class PostMarker(models.Model):
    messageid = models.CharField(max_length=80, editable=False, null=False)
    person_id = models.CharField(max_length=180, editable=False, null=False)
    is_good = models.BooleanField(blank=True)

    class Meta:
        db_table = 'spotnet_marker'
        verbose_name = _('watched post')
        unique_together = (('messageid','person_id',),)

    @property
    def person(self):
        t,pid = self.person_id[0], self.person_id[1:]
        if t == '#':
            return User.objects.get(pk=pid)
        elif t == '$':
            return pid
        else:
            raise ValueError("Invalid value found for PostMarker.person_id.")





class PostDownloaded(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'spotnet_downloaded'
        verbose_name = _('downloaded post')
        unique_together = (('user','post',),)





