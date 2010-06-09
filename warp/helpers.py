import sys, urllib, urllib2

from twisted.python import util, filepath

from mako.template import Template

from warp.runtime import store, templateLookup, config, exposedStormClasses



def getNode(name):

    bits = name.split('/')
    leaf = bits[-1]

    try:
        return getattr(__import__("nodes.%s" % ".".join(bits), 
                                  fromlist=[leaf]), 
                       leaf, None)
    except ImportError, ie:
        # Hrgh
        if ie.message.startswith("No module named"):
            return None
        raise


def getCrudClass(cls):
    return exposedStormClasses[cls.__name__][1]

def getCrudObj(obj):
    return getCrudClass(obj.__class__)(obj)


def getCrudNode(crudClass):
    # XXX WHAT - God, what *should* this do??
    return sys.modules[crudClass.__module__]

    

def renderTemplateObj(request, template, **kw):
    return template.render(node=request.node,
                           request=request,
                           store=store,
                           facet=request.resource.facetName,
                           args=request.resource.args,
                           **kw)


def renderTemplate(request, templatePath, **kw):
    template = Template(filename=templatePath,
                        lookup=templateLookup,
                        format_exceptions=True,
                        output_encoding="utf-8")
    return renderTemplateObj(request, template, **kw)


def renderLocalTemplate(request, filename, **kw):
    templatePath = util.sibpath(request.node.__file__, filename)
    return renderTemplate(request, templatePath, **kw)


def url(node, facet="index", args=(), query=()):
    nodeDir = filepath.FilePath(node.__file__).parent()
    segments = nodeDir.segmentsFrom(config['siteDir'].child("nodes"))
    segments.append(facet)
    segments.extend(args)
    u = "/%s" % ("/".join(map(str, segments)))
    if query:
        u = "%s?%s" % (u, urllib.urlencode(query))
    return u
        

def link(label, node, facet="index", args=(), query=(), **attrs):
    attrs['href'] = url(node, facet, args, query)
    bits = " ".join('%s="%s"' % (k.rstrip('_'), v) for (k,v) in attrs.iteritems())
    return '<a %s>%s</a>' % (bits, label)


def button(label, node, facet="index", args=[], confirm=None):
    action = "javascript:document.location.href='%s';" % url(node, facet, args)
    if confirm is not None:
        action = "if (confirm('%s')) { %s }" % (confirm, action)
    return '<input type="button" value="%s" onclick="%s">' % (label, action)
