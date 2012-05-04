import pySpotnet.nntplib, \
       pySpotnet.NZBFetcher, \
       pySpotnet.Spot, \
       pySpotnet.SpotFetcher, \
       pySpotnet.SpotHeader



news_servers = (
    ("news2.neva.ru", 119, None, None),
    ("news2.neva.ru", 119, "", ""),
    ("news.hitnews.eu", 119, "christianvanratingen", "xfwwanf7"),
)


def get_news_server(id):
    try:
        server = news_servers[id]
    except:
        raise ValueError("The id '%s' does not identify a news server!"%id)
    try:
        conn = pySpotnet.nntplib.NNTP(host=server[0], port=server[1], user=server[2], password=server[3])
    except:
        raise
        raise Exception("Unable to connect to server '%s'!"%server[0])
    else:
        return conn





def spot_finder(start, stop, server_id=0, msg_every=1000):
    # connect to server
    news_server = get_news_server(server_id)
    spot_fetcher = pySpotnet.SpotFetcher.SpotFetcher(news_server)
    # iterate new spots
    for x in xrange(start, stop):
        try:
            for s in spot_fetcher.get_spot_headers(x, x+1):
                pass
        except pySpotnet.nntplib.NNTPTemporaryError:
            if x%msg_every == 0:
                print 'Tried', x, '...'
        else:
            print 'Found working number:', x
            return



def spot_available(num, fetcher):
    try:
        for s in fetcher.get_spot_headers(num, num+1):
            pass
    except pySpotnet.nntplib.NNTPTemporaryError:
        return False
    else:
        return True

def smart_spot_finder(start, stop, fetcher=None, server_id=0):
    "Retuns the lowest number of post that is available within [start,stop], None if no available post found"
    start,stop = int(start),int(stop)
    if start > stop:
        raise ValueError("Start > stop!")
    if fetcher is None:
        # connect to server
        server = get_news_server(server_id)
        fetcher = pySpotnet.SpotFetcher.SpotFetcher(server)
    # start looking for available spot
#    if spot_available(start, fetcher) is True:
#        return start
#    if start == stop:
#        return None
#    elif start + 1 == stop:
#        if spot_available(stop, fetcher) is True:
#            return stop
#        else:
#            return None
#    else:
#        mid = (start+stop)/2
#        h1 = smart_spot_finder(start+1, mid, fetcher)
#        if h1 is not None:
#            return h1
#        print 'First available post >', mid
#        h2 = smart_spot_finder(mid+1, stop, fetcher)
#        if h2 is not None:
#            return h2
#        else:
#            return None
    if start == stop:
        x = spot_available(start, fetcher)
        if x is False:
            print 'First available post is not', start
            return None
        else:
            print 'First available post is', start
            return start
    else:
        mid = (start+stop)/2
        if spot_available(mid, fetcher):
            print 'First available post <', mid
            return smart_spot_finder(start, mid-1, fetcher)
        else:
            print 'First available post >', mid
            return smart_spot_finder(mid+1, stop, fetcher)



def get_spot(id, fetcher=None, server_id=0):
    if fetcher is None:
        # connect to server
        server = get_news_server(server_id)
        fetcher = pySpotnet.SpotFetcher.SpotFetcher(server)
    return fetcher.get_spot(id)
    


def print_spot(spot):
    print "================"
    print "Spot id %s" % spot.id
    print "----------------"
    for a in ('title','poster','description','tag','timestamp','message_id','category','subcategory','image','website','size','nzb',):
        print "%s: %s" % (a.upper(), getattr(spot,a))
    print "================"


def print_spot_attr_types(spot):
    print "================"
    print "----------------"
    for a in ('id','message_id','title','poster','description','tag','timestamp','message_id','category','subcategory','image','website','size','nzb',):
        print "%s: %s" % (a.upper(), type(getattr(spot,a)))
    print "================"


def main_prev():
    # connect to server
    news_server = get_news_server(2)
    spot_fetcher = pySpotnet.SpotFetcher.SpotFetcher(news_server)
    # iterate new spots
    added_count = 0
    START = 0
    for s in spot_fetcher.get_spot_headers(START, START+1):
        spot = spot_fetcher.get_spot(s.message_id)

        added_count += 1
    return added_count





def main():
    #spot_finder(0, 99999999)

    #fp = smart_spot_finder(0, 999999, server_id=2)
    #print 'First available post:', fp

    #spot_finder(64900,66100, server_id=2)

    spotid = 1
    #print 'Spot %s:'%spotid, get_spot(spotid, server_id=2)
    #print_spot(get_spot(spotid, server_id=2))
    #print_spot_attr_types(get_spot(spotid, server_id=2))

    #print 'Main return:', main()
    
def shell():
    #spotid = 1
    #from models import SpotnetPost
    #snp = SpotnetPost.from_spot(get_spot(spotid, server_id=2))
    #snp.save()

    pass








if __name__ == '__main__':
    main()
