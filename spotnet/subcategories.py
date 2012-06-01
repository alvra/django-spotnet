from django.utils.translation import ugettext as _, ugettext_noop
import settings


UNKNOWN_TEXT = ugettext_noop('unknown')


def split_code(code):
    i = 0
    while code[i].isdigit():
        i += 1
    j = i
    while code[j].isalpha():
        j += 1
    return int(code[:i]), code[i:j], int(code[j:])


class Subcategory(object):
    def __init__(self, code):
        self.code = code
        try:
            self._main, self._type, self._sub = split_code(code)
        except:
            raise ValueError("Got an invalid subcategory code %r" % self.code)

    def is_valid(self):
        return self._main  in settings.CATEGORY_MAPPING \
            and self._type in settings.SUBCATEGORY_TYPE_MAPPING[self._main] \
            and self._sub  in settings.SUBCATEGORY_MAPPING[self._main][self.type_base]

    @property
    def main(self):
        return _(settings.CATEGORY_MAPPING.get(self._main, UNKNOWN_TEXT))

    @property
    def type_base(self):
        cmap = settings.SUBCATEGORY_TYPE_MAPPING.get(self._main, {})
        return cmap.get(self._type, UNKNOWN_TEXT)

    @property
    def type(self):
        return _(self.type_base)

    @property
    def sub(self):
        cmap = settings.SUBCATEGORY_MAPPING.get(self._main, {})
        ccmap = cmap.get(self.type_base, {})
        return _(ccmap.get(self._sub, UNKNOWN_TEXT))

    def __unicode__(self):
        return self.sub
