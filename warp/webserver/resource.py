import os.path

from zope.interface import implements

from twisted.web.resource import IResource
from twisted.web.error import NoResource
from twisted.web import static
from twisted.python.filepath import FilePath, InsecurePath

from warp.webserver import auth, comet
from warp.runtime import config, store, templateLookup
from warp import helpers


if '.ico' not in static.File.contentTypes:
    static.File.contentTypes['.ico'] = 'image/vnd.microsoft.icon'


class WarpResourceWrapper(object):
    implements(IResource)

    isLeaf = False

    def __init__(self):
        lookupDir = config['siteDir'].child("templates").path
        templateLookup.__init__(directories=[lookupDir])


    def getChildWithDefault(self, firstSegment, request):

        if firstSegment:
            fp = self.buildFilePath(request)
            if fp is not None:
                del request.postpath[:]
                return static.File(fp.path)

        session = request.getSession()
        if session is not None:
            request.avatar = session.avatar

        if firstSegment == '__login__':
            return auth.LoginHandler()
        elif firstSegment == '__logout__':
            return auth.LogoutHandler()
        elif firstSegment == '_comet':
            return NodeResource(comet)
        elif not firstSegment:
            return Redirect(config['default'])

        return self.getNode(firstSegment)


    def buildFilePath(self, request):
        filePath = config['siteDir'].child('static')
        for segment in request.path.split('/'):
            try:
                filePath = filePath.child(segment)
            except InsecurePath:
                return None

        if filePath.exists() and filePath.isfile():
            return filePath


    def getNode(self, name):
        node = getattr(__import__("nodes", fromlist=[name]), name, None)
        
        if node is None:
            return NoResource()

        return NodeResource(node)


class Redirect(object):
    implements(IResource)

    isLeaf = True

    def __init__(self, url):
        self.url = url

    def render(self, request):
        request.redirect(self.url)
        return "Redirecting..."



class NodeResource(object):
    implements(IResource)

    # You can always add a slash
    isLeaf = False


    def __init__(self, node):
        self.node = node
        self.facetName = None
        self.args = []
        

    def getChildWithDefault(self, segment, request):
        self.facetName = segment
        self.isLeaf = True
        return self

            
    def render(self, request):
        self.args = request.postpath            

        if not self.facetName:
            request.redirect(request.childLink('index'))
            return "Redirecting..."

        request.node = self.node

        renderFunc = getattr(self.node, 'render_%s' % self.facetName, None)
        if renderFunc is not None:
            return renderFunc(request)

        templatePath = self.getTemplate()
        if templatePath is not None:
            return helpers.renderTemplate(request, templatePath.path)

        return NoResource().render(request)


    def getTemplate(self):
        templatePath = FilePath(
            self.node.__file__
            ).sibling(self.facetName + ".mak")

        if templatePath.exists():
            return templatePath


    def __repr__(self):
        return "<NodeResource: %s::%s (%s)>" % (
            self.node.__name__, self.facetName, self.args)
