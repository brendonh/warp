from twisted.python import util

from mako.template import Template

from warp.runtime import store, templateLookup


def renderTemplate(request, templatePath, **kw):
    template = Template(filename=templatePath,
                        lookup=templateLookup,
                        format_exceptions=True)

    return template.render(node=request.node,
                           request=request,
                           store=store,
                           **kw)


def renderLocalTemplate(request, filename, **kw):
    templatePath = util.sibpath(request.node.__file__, filename)
    return renderTemplate(request, templatePath, **kw)
