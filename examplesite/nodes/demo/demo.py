from twisted.internet import defer, reactor
from twisted.web.server import NOT_DONE_YET

def render_incode(request):
    d = defer.Deferred()

    def finished(result):
        request.write("After a while, I got: %s" % result)
        request.finish()

    d.addCallback(finished)

    reactor.callLater(5, lambda: d.callback("Yay for deferreds"))

    return NOT_DONE_YET



def render_startCounter(request):
    reactor.callLater(1, lambda: _nextCometMessage(request))
    return "ok"



counter = 0

def _nextCometMessage(request):
    from warp.webserver.comet import get_session
    session = get_session(request)
    if session is None:
        return

    global counter
    counter += 1
    session.push({"key": "message", 'counter': counter})
    reactor.callLater(1, lambda: _nextCometMessage(request))

