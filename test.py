from connection import SpotnetConnection
from models import SpotnetPost
from post import iter_test_posts
from pprint import pprint





def test_updating():
    c = SpotnetConnection(log_print=True, log_logging=False)
    print 'Connected:', c.is_connected()

    print 'Starting updating...'
    c.update()
    print 'Done updating!'



def test_parsing():
    n = 0
    for post in iter_test_posts():
        if n == 1: break
        print 'testing post %s' % post.messageid
        import pprint
        pprint.pprint(post._rawpost)
        n += 1



def test_get_raw_post():
    #messageid = '<50d0acd6326548698ba398f6faa3c10b14@free.pt>'
    messageid = '<81uAKb8aRqYgpgTTgA1Id@spot.net>'

    c = SpotnetConnection(log_print=True, log_logging=False)
    print 'Connected:', c.is_connected()

    print 'Getting post...'
    post = c.get_raw_post(messageid)
    print 'Got post!'

    print 'Subcategories:'
    print post.subcategories



def test_get_nzb_base(snp_index=0):
    snp = SpotnetPost.objects.order_by('-posted').only('messageid')[snp_index]
    c = SpotnetConnection(log_print=True, log_logging=False)
    nzb_file = '/home/alexander/Desktop/test.nzb'
    print "Post is %s" % repr(snp)
    print "With messageid '%s'" % snp.messageid
    print "Nzb attr is '%s'" % repr(snp.nzb)
    print 'Getting nzb...'
    nzb_content = snp.get_nzb_content(connection=c)
    if nzb_content:
        print 'Got nzb!'
        with open(nzb_file, 'w') as f:
            f.write(nzb_content)
        print "nzb witten to '%s'" % nzb_file
    else:
        print 'Didn\'t get nzb!'

def test_get_nzb():
    count = 5
    for x in xrange(count):
        print
        test_get_nzb_base(x)
    
    
    
    
    
    
    
    



def main():
    test_updating()
    #test_parsing()
    #test_get_raw_post()
    #test_get_nzb()
    #test_get_nzb_base()



if __name__ == '__main__':
    main()

