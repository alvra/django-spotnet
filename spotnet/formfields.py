from django import forms


class StringSetFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.split_char = kwargs.pop('split_char', ',')
        kwargs['widget'] = StringSetFormWidget(split_char=self.split_char)
        super(StringSetFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(StringSetFormField, self).clean(value)
        return (x.strip() for x in value.split(self.split_char))


class StringSetFormWidget(forms.widgets.TextInput):
    def __init__(self, **kwargs):
        self.split_char = kwargs.pop('split_char', ',')
        if not self.split_char.endswith(' '):
            self.split_char += ' '
        super(StringSetFormWidget, self).__init__(**kwargs)

    def _format_value(self, value):
        if isinstance(value, basestring):
            return value
        try:
            return self.split_char.join(value)
        except TypeError:
            return super(StringSetFormWidget, self)._format_value(value)
