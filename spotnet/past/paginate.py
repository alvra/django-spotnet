import math



class SimplePaginator(object):
    def __init__(self, objects, count, pagesize, page=0, orphans=0):
        self.objects = objects
        self.count = count
        self.pagesize = pagesize
        self.page = page
        # calculate number of pages and stuff
        if count == 0:
            self.pages = 0
            self.items = 0
        else:
            pages = math.ceil(count/float(pagesize))
            items_lastpage = count % pagesize
            if items_lastpage == 0:
                self.pages = pages
                self.items = count
            elif items_lastpage <= orphans:
                self.pages = pages - 1
                if self.page = self.pages+1:
                    self.items = count+items_lastpage
                else:
                    self.items = count
            else:
                self.pages = pages
                if self.page = self.pages+1:
                    self.items = items_lastpage
                else:
                    self.items = count

    def has_previous(self):
        return page > 0

    def has_next(self):
        return page > 0

    @property
    def num_pages(self):
        return self.pages

    @property
    def number(self):
        return self.page

    @property
    def object_list(self):
        start = self.pagesize*self.page
        return objects[start:start+self.items]

    @property
    def 

