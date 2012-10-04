import traceback
from collections import defaultdict

from storm.locals import Store, Storm
from storm.info import get_obj_info


handlers = defaultdict(list)

def handler(event, *models):
    if not models:
        models = [None]
    else:
        models = [model.__name__ for model in models]

    def decorate(fun):
        for modelName in models:
            handlers[(modelName, event)].append(fun)
        return fun

    return decorate



class CommitEventStore(Store):

    def __init__(self, database, cache=None):
        self.events = []
        super(CommitEventStore, self).__init__(database, cache)

    def rollback(self):
        self.events = []
        super(CommitEventStore, self).rollback()

    def commit(self):
        super(CommitEventStore, self).commit()

        # Event handlers can emit new events, which will run after
        # all existing events are handled. Do a little dance here
        # to make this clean.
        while self.events:
            events = self.events
            self.events = []
            for event in events:
                event.run()


                
class EventModel(Storm):
    
    def emit(self, event):
        store = get_obj_info(self)["store"]
        if store is None:
            raise Exception("Tried to emit event for store-less object")

        store.events.append(PendingEvent(self, event))



class PendingEvent(object):
    def __init__(self, obj, event):
        self.obj = obj
        self.event = event

    def run(self):
        modelName = self.obj.__class__.__name__
        eventHandlers = (set(handlers.get((modelName, self.event), [])) 
                         | set(handlers.get((None, self.event), [])))

        for handler in eventHandlers:
            try:
                handler(self.obj)
            except Exception:
                print ">>> Error in event handler"
                traceback.print_exc()
