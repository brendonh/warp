import pytz

from storm.locals import *

from twisted.internet import defer, reactor
from twisted.web.server import NOT_DONE_YET


class Person(Storm):    
    id = Int(primary=True)
    name = Unicode()
    birthdate = DateTime(tzinfo=pytz.UTC)


def render_incode(request):
    d = defer.Deferred()

    def finished(result):
        request.write("After a while, I got: %s" % result)
        request.finish()

    d.addCallback(finished)

    reactor.callLater(5, lambda: d.callback("Yay for deferreds"))

    return NOT_DONE_YET
