from math import ceil
from django.core.paginator import Paginator as BasePaginator, InvalidPage, EmptyPage, PageNotAnInteger

# slight edit of the django paginator
# optimized for large object_lists
# and avoids counting them all





# This is not in use
# since it's slower then the original Django implementation

class Paginator(object):
    def __init__(self, object_list, per_page, allow_empty_first_page=None):
        self.object_list = object_list
        self.per_page = int(per_page)

    def validate_number(self, number):
        "Validates the given 1-based page number."
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        return number

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        page_object_list = self.object_list[bottom:top]
        if len(page_object_list) == 0:
            raise EmptyPage('That page contains no results')
        return Page(page_object_list, number, self)

    def has_object(self, index):
        try:
            self.object_list[index]
        except:
            return False
        else:
            return True

    def has_page(self, number):
        # if there is an object on that page, it exists
        return self.has_object(number * self.per_page)



class Page(object):
    def __init__(self, object_list, number, paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator

    def __repr__(self):
        return '<Page %s>' % self.number

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        # The object_list is converted to a list so that if it was a QuerySet
        # it won't be a database hit per __getitem__.
        return list(self.object_list)[index]

    # The following four methods are only necessary for Python <2.6
    # compatibility (this class could just extend 2.6's collections.Sequence).

    def __iter__(self):
        i = 0
        try:
            while True:
                v = self[i]
                yield v
                i += 1
        except IndexError:
            return

    def __contains__(self, value):
        for v in self:
            if v == value:
                return True
        return False

    def index(self, value):
        for i, v in enumerate(self):
            if v == value:
                return i
        raise ValueError

    def count(self, value):
        return sum([1 for v in self if v == value])

    # End of compatibility methods.

    def has_next(self):
        return self.paginator.has_page(self.number+1)

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def next_page_number(self):
        return self.number + 1

    def previous_page_number(self):
        return self.number - 1



