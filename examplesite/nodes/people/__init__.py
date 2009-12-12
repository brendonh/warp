try:
    import json
except ImportError:
    import simplejson as json

from storm.locals import Desc

from warp.runtime import store
from warp import helpers

from models import Person


def render_index(request):
    people = store.find(Person).order_by(Person.name)
    return helpers.renderLocalTemplate(request, "index.mak", 
                                       people=people)


def render_list_json(request):

    params = dict((k, request.args.get(k, [''])[0])
                  for k in ('_search', 'page', 'rows', 'sidx', 'sord'))

    # XXX Todo -- Search

    sortCol = getattr(Person, params['sidx'])
    if params['sord'] == 'desc':
        sortCol = Desc(sortCol)

    rowsPerPage = int(params['rows'])
    start = (int(params['page']) - 1) * rowsPerPage
    end = start + rowsPerPage

    totalResults = store.find(Person).count()
    
    results = list(store.find(Person).order_by(sortCol)[start:end])

    rows = [{'id': row.id, 
             'cell': [str(row.id), row.name, row.birthdate.strftime("%x %H:%M")]}
            for row in results]

    obj = {
        'total': str(totalResults),
        'page': params['page'],
        'records': str(len(results)),
        'rows': rows,
    }

    return json.dumps(obj)
