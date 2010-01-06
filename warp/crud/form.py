from warp.runtime import store, exposedStormClasses
from warp.helpers import getCrudClass

def applyForm(objects, request):

    errors = []
    actions = []
    results = {
        'created': [],
        'updated': [],
        'deleted': [],
    }

    for jsobj in objects:

        if not all(jsobj.get(k) for k in ('action', 'model')):
            raise ValueError("Invalid object: %s" % jsobj)
            
        try:
            model, crudClass = exposedStormClasses[jsobj['model']]
        except KeyError:
            errors.append((None, u"Unknown or unexposed model: %s" % jsobj['model']))
            continue


        if jsobj['action'] == 'create':
            obj = model()
            store.add(obj)
            obj.fakeID = '*' + jsobj['id']
            results['created'].append(obj)

        else:

            try:
                objID = int(jsobj['id'])
            except ValueError:
                errors.append((None, u"Invalid id: %s" % jsobj['id']))
                continue

            obj = store.get(model, objID)
            if obj is None:
                errors.append((None, u"Missing ID '%s' for model '%s'" % (jsobj['id'], jsobj['model'])))
                continue

            results['updated'].append(obj)


        for (key, val) in jsobj['fields'].iteritems():
            try:
                attr = str(key)
            except UnicodeEncodeError:
                errors.append((None, u"Invalid field name '%s'" % attr))
                continue

            # XXX TODO -- Access check goes here (or, uh, somewhere)
            # ...

            crud = crudClass(obj)
            actions.append( (crud, attr, val) )


    if errors:
        return (False, errors)

    for (crud, attr, val) in actions:
        error = crud.save(attr, val, request)
        if error is not None:
            key = crud.getProxy(attr, request).fieldName()
            errors.append((key, error))

    if errors:
        return (False, errors)

    return (True, results)
