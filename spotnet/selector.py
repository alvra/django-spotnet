from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.translation import ugettext as _


class Selector(object):
    checkbox_template = '<input type="checkbox" name="%(name)s" value="%(value)s" />'
    action_input_name = 'selector_action'
    checkbox_true_val = 'on'

    def __init__(self, objects, actions):
        self._objects = objects
        self._actions = actions

    def apply_action(self, request):
        posted = dict(request.POST)
        action_name = posted.pop(self.action_input_name, [None])[0]
        action = self._actions.get(action_name, None)
        selection = self.get_selection((k for k, v in posted.iteritems() if v[0] == self.checkbox_true_val))
        # this is way to generic, the actions should do this themselves
        # since they can provide a more detailed message
        #if len(selection) == 0:
        #    return _("Could not apply action since nothing was selected.")
        if action_name and action:
            return action.apply(request, selection)
        else:
            return None

    def get_object_id(self, obj):
        raise NotImplementedError("The 'get_object_id' method of this " \
            "Selector is not implemented")

    def get_selection(self, obj):
        raise NotImplementedError("The 'get_selection' method of this " \
            "Selector is not implemented")

    def get_checkbox(self, obj):
        return mark_safe(self.checkbox_template % dict(
            name=conditional_escape(self.get_object_id(obj)),
            value=self.checkbox_true_val,
        ))

    def get_row(self, obj):
        return SelectorRow(self.get_checkbox(obj), obj)

    def __iter__(self):
        for o in self._objects:
            yield object.__getattribute__(self, 'get_row')(o)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except (TypeError, AttributeError):
            return getattr(object.__getattribute__(self, '_objects'), name)

    def action_selector(self):
        x = ['<select name="%s">' % self.action_input_name]
        for action_name, action in self._actions.iteritems():
            x.append('<option value="%(val)s">%(title)s</option>' % dict(
                val=action_name,
                title=conditional_escape(action.title()),
            ))
        x.append('</select>')
        return mark_safe(''.join(x))


class QuerySelector(Selector):

    # this is needed to mimic some of the QuerySet behavior
    # as is required by using paginators

    def get_object_id(self, obj):
        return 'post_%s' % obj.pk

    def get_id_pk(self, id):
        try:
            return int(id[5:])
        except:
            return None

    def get_selection(self, ids):
        pks = (self.get_id_pk(i) for i in ids)
        return [i for i in pks if i is not None]

    def __len__(self):
        return len(object.__getattribute__(self, '_objects'))

    def __getitem__(self, key):
        if isinstance(key, slice):
            return type(self)(object.__getattribute__(self, '_objects').__getitem__(key), self._actions)
        else:
            return self.get_row(object.__getattribute__(self, '_objects').__getitem__(key))


class SelectorRow(object):
    def __init__(self, checkbox, obj):
        self._checkbox = checkbox
        self._object = obj

    def __getattribute__(self, name):
        if name == 'checkbox':
            return object.__getattribute__(self, '_checkbox')
        else:
            return getattr(object.__getattribute__(self, '_object'), name)
