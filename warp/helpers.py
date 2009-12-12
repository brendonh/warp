from mako.template import Template

from warp.runtime import store, templateLookup


def renderTemplate(request, templatePath):
    template = Template(filename=templatePath,
                        lookup=templateLookup,
                        format_exceptions=True)

    return template.render(node=request.node,
                           request=request,
                           store=store)
