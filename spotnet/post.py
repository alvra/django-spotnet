import logging
from xml.dom.minidom import parseString
from datetime import datetime





class InvalidPost(Exception):
    pass





class RawPost(object):

    # PUBLIC ATTRIBUTES:
    # messageid     : string, like <xxx@spot.net>
    # postnumber    : integer (server dependent!)
    # poster        : string, name of the poster
    # title         : string, post title
    # description   : string, post description
    # tag           : string or None, post tag
    # posted        : datetime.datetime, post creation moment
    # category      : int, indication of category
    # subcategory   : (possibly empty) list of strings, indication of subcategories
    # image         : string or None, http adress of post image
    # website       : sting or None, http adress of additional post info
    # size          : int or None, byte size of files in post
    # nzb           : list of strings, messageids of posts that, together, contain the nzb file
    #                  use a RawNzbPost object to get the actual nzb file from these messageids
    #
    # PUBLIC METHODS:
    # verify_post()     : bool, 
    # verify_poster()   : bool, 
    #

    # RAW POST DESCRIPTION:
    # [0] : '220 0 <0d7IZVT9wjIJqcSTgAYLN@spot.net> article' : status ? messageid type
    # [1] : '0' : ?
    # [2] : '<0d7IZVT9wjIJqcSTgAYLN@spot.net>' : messageid
    # [3] : '...' : body
    # body:
    # NOTE THAT SOME HEADERS ARE SPREAD OVER SEVERAL LINES!
    # - Path                        : 'news.hitnews.eu!not-for-mail'
    # - From                        : 'kww <132200@13a05b03.42638314.132200.1309845303.JnY.so8.POWbpJxp9q5FWkRbrq8aDIbCAvdBkK0XmV9mpTIswr9SL8FlU28vtJYtnEuS-sqx-s>'
    # - Subject
    # - Newsgroups
    # - Message-ID
    # - X-XML
    # - X-XML
    # - X-XML-Signature             : 'cUWupZtWsQAhp4WLYg-pwT00ab-sJvdMQnKWu1kDETInZowAc06x-pBW3-sIWT0D7VuQ' : signature of xml
    # - X-User-Key                  : '<RSAKeyValue><Modulus>szsAIT5lVEzonnwg81DoU/44KTXkdIYrAdAFpoB/99Fw0VC6QVad7PRKgDPFeDW5</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>'
    # - X-User-Signature            : 'Mh-sbcEHnIR-pNRVHFtPP-sxHTTTFu7S1vkmOterGBKGNCIcwyN5Xo7BQxaFtq0FgRd'
    # - Content-Type                : 'text/plain; charset=ISO-8859-1' : mime-type; encoding
    # - Content-Transfer-Encoding   : '8bit' : ?
    # - Date
    # - Lines                       : Number of lines following headers that make up the body
    # - Organization                : Organization that originally posted this post
    # - NNTP-Posting-Host           : == Organization(?)
    # - X-Complaints-To             : Email adress to notify in case of abuse
    # [empty line]
    # Remaining lines (>1!) make up the body
    #    the amount of lines here is passed as header 'Lines'

    def __init__(self, postnumber, rawpost):
        self.postnumber = int(postnumber) if postnumber is not None else None
        self.messageid = rawpost[2]
        self._rawpost = rawpost
        try:
            self.content = self.parse_rawpost_content(self._rawpost[3])
        except InvalidPost:
            raise
        except Exception as e:
            raise InvalidPost("Error in parsing raw post content, exception was '%s'" % e)
        try:
            xml_data = self.content['X-XML']
        except KeyError:
            raise InvalidPost("Post has no X-XML header")
        try:
            self.extra = self.parse_xml_content(xml_data)
        except InvalidPost:
            raise
        except:
            print 'Error in parsing raw post content'

    def parse_rawpost_content(self, content):
        d = {}
        content_length = len(content)
        l = -1
        # find Lines header
        for num,line in enumerate(content):
            if line.startswith('Lines: '):
                l = num
                break
        if l == 0:
            raise InvalidPost("Post does not have a Lines header.")
        body_lines = int(content[l][len('Lines: '):])
        for l in xrange(len(content)-body_lines-1):
            if ':' in content[l]:
                k,v = content[l].split(': ', 1)
                if k in d:
                    d[k] += v
                else:
                    d[k] = v
            else:
                # we only allow an empty line here!
                if content[l] != '':
                    raise InvalidPost("Post has invalid header line '%s'" % content[l])
            l += 1
        if not content[l] == '':
            raise InvalidPost("First line after headers is not empty!")
        if not len(content) == int(d['Lines']) + l + 1:
            raise InvalidPost("Header value for Lines differs from actual number of lines!")
        return d

    def parse_xml_content(self, xml_string):
        try:
            xml = parseString(xml_string)
        except:
            raise InvalidPost("Post has invalid XML data for header X-XML")
        doc = xml.documentElement
        if not doc.tagName == 'Spotnet':
            raise InvalidPost("XML for spotnet post does not have a main node called 'Spotnet'")
        if not len(doc.childNodes) == 1:
            raise InvalidPost("XML for spotnet post does not have 1 child for main node 'Spotnet'")
        main = doc.childNodes[0]
        if not main.tagName == 'Posting':
            raise InvalidPost("XML for spotnet post does not have a main child node called 'Posting' for 'Spotnet'")
        # assemble dict of content
        d = {}
        for e in main.childNodes:
            if len(e.childNodes) == 1 and e.childNodes[0].nodeType in (3,4):
                # if it has one child that is a textnode or cdata node, add it to the dict
                d[e.tagName] = e.childNodes[0].nodeValue
            elif e.tagName == 'Category':
                d['Category'] = []
                d['Subcategories'] = []
                for cat_node in e.childNodes:
                    if cat_node.nodeType == 3:
                        # a main category
                        d['Category'].append(cat_node.nodeValue)
                    if cat_node.nodeType == 1:
                        # a sub category
                        d['Subcategories'].append(cat_node.childNodes[0].nodeValue)
            elif e.tagName == 'NZB':
                # we give this nzb dict the same name as the tag
                # so that _if_ an nzb only contains one textnode with
                # the location, the result is similar (a string instead of a string list)
                d['NZB'] = []
                for nzb_node in e.childNodes:
                    if not nzb_node.tagName == 'Segment':
                        raise InvalidPost("XML for spotnet post, in NZB node there are child nodes that are not named 'Segment'")
                    d['NZB'].append(nzb_node.childNodes[0].nodeValue)
        if isinstance(d.get('Category', None), list):
              if len(d['Category']) == 0:
                  d['Category'] = None
              else:
                  d['Category'] = d['Category'][0]
        if isinstance(d.get('NZB', None), basestring):
              d['NZB'] = [d['NZB']]
        return d

    def parse_date(self, date):
        # p is of form 'Mon, 06 Jun 2011 17:56:39 +0200'
        return NotImplemented

    def decode_string(self, string):
        return string

    # public properties

    @property
    def poster(self):
        p = self.content['From'].split('<', 1)[0].strip()
        assert p == self.extra['Poster']
        return self.decode_string(self.extra['Poster'])

    @property
    def subject(self):
        return self.extra['Title']
        # the following has been deprecated because
        # (same reason as description)
        subj = self.content['Subject']
        if ' | ' in subj:
            subj, poster = subj.split(' | ',1)
        assert subj == self.extra['Title']
        #assert poster == self.extra['Poster'] # this is not True
        return self.decode_string(self.extra['Title'])

    @property
    def description(self):
        return self.decode_string(self.extra['Description'])
        # the following has been deprecated because
        # the xml description a mucht better
        # and simpler way of obtaining the title
        # without any immediate encoding errors
        desc = ''.join(self._rawpost[3][-int(self.content['Lines']):])
        assert desc == self.extra['Description']
        return self.decode_string(self.extra['Description'])

    @property
    def tag(self):
        return self.decode_string(self.extra.get('Tag', None))

    @property
    def posted(self):
        # TODO:
        # This has to be rewritten to use django's new timezone support.
        # The NNTP-Posting-Date header is not mandatory, but does contain
        # timezonde data (always?) and can thus be used to get the tz.
        # If that's not available, another fallback is the Created
        # header can supply the creation datetime, but it does not contain
        # timezone info, so we must make assumptions.
        # Note that the 'Date' header is the only one usefull here
        # that is required, but does not supply time info.

        # this creates a datetime object
        # of the systems timezone
        # wich is further handled correctly by django
        dt = self.extra.get('Created', None)
        try:
            dt = float(dt)
        except ValueError:
            dt = None
        if dt:
            return datetime.fromtimestamp(dt)
        else:
            return None
        # the following has been deprecated because
        # (same reason as description)
        p = self.content.get('NNTP-Posting-Date', None)
        # A Date sometimes added by the NNTP server in case the current server date is different to the date provided by the news client.
        # source: http://tgos.org/newbie/xheader.html
        if p is None:
            p = self.get('Date')
        date = self.parse_date(p)
        assert date == datetime.fromtimestamp(self.extra.get['Created'])
        return date

    @property
    def category(self):
        return self.extra.get('Category', None)

    @property
    def subcategories(self):
        return self.extra.get('Subcategories', [])

    @property
    def image(self):
        return self.extra.get('Image', None)

    @property
    def website(self):
        return self.extra.get('Website', None)

    @property
    def size(self):
        return self.extra.get('Size', None)

    @property
    def nzb(self):
        return self.extra.get('NZB', [])





