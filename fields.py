from django.db import models
from django.utils.translation import ugettext as _
from formfields import StringSetFormField





#class StringSetField(models.CommaSeparatedIntegerField):
class StringSetField(models.CharField):
    """A field that holds a set of strings.
    Subclass of CommaSeparatedIntegerField since the internal storage is the same.
    """

    description = "A field that holds a set of strings"

    __metaclass__ = models.SubfieldBase

    def __init__(self, **kwargs):
        error_messages = kwargs.pop('error_messages', {})
        if not 'invalid' in error_messages:
            error_messages['invalid'] = _('Enter only text separated by commas.')
        kwargs['error_messages'] = error_messages
        return super(StringSetField, self).__init__(**kwargs)

    def to_python(self, value):
        # from a db value to a python object
        if isinstance(value, (list, set, tuple)) or hasattr(value, '__iter__'):
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

    def value_to_string(self, obj):
        return ', '.join(obj)

    def formfield(self, **kwargs):
        return StringSetFormField(**kwargs)





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





