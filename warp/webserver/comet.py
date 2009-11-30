import uuid, json

from twisted.internet import reactor
from twisted.web.server import NOT_DONE_YET

sessions = {}

SESSION_TIMEOUT = 31
POLL_TIMEOUT = 10


class CometSession(object):

    def __init__(self, sid):
        self.id = sid
        self.buffer = []
        self.listener = None
        self.pollTimeout = None
        
        self.sessionTimeout = reactor.callLater(
            SESSION_TIMEOUT, self.cbSessionTimeout)


    def addListener(self, request):

        self.sessionTimeout.reset(SESSION_TIMEOUT)

        if self.buffer:
            assert self.listener is None
            msg = json.dumps(self.buffer)
            self.buffer[:] = []
            return msg

        if self.listener is not None:
            self._flushWith([])

        self.listener = request
        self.pollTimeout = reactor.callLater(
            POLL_TIMEOUT, self.cbPollTimeout)

        return NOT_DONE_YET

            
    def push(self, obj):
        if self.listener is not None:
            self._flushWith([obj])
        else:
            self.buffer.append(obj)


    def cbSessionTimeout(self):
        print "Comet session expired:", self.id
        del sessions[self.id]
        

    def cbPollTimeout(self):
        self._flushWith([], True)


    def _flushWith(self, stuff, isTimeout=False):
        msg = json.dumps(stuff)
        self.listener.write(msg)
        self.listener.finish()
        self.listener = None
        if not isTimeout:
            self.pollTimeout.cancel()




def get_session(request, createIfMissing=False):
    sid = request.args['id'][0]
    try:
        return sessions[sid]
    except KeyError:
        if createIfMissing:
            session = CometSession(sid)
            sessions[sid] = session
            return session



def render_id(request):
    return str(uuid.uuid4())



def render_longpoll(request):
    return get_session(request, True).addListener(request)
    

def render_testpush(request):
    session = get_session(request, True)
    session.push({'key': 'value'})
    return "Ok"
