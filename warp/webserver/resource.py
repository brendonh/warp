import os.path

from zope.interface import implements

from twisted.python import util
from twisted.python.filepath import FilePath, InsecurePath

from twisted.web.resource import IResource
from twisted.web.error import NoResource
from twisted.web import static

from warp.common import access, translate
from warp.webserver import auth, comet
from warp.runtime import config, store, templateLookup
from warp import helpers


if '.ico' not in static.File.contentTypes:
    static.File.contentTypes['.ico'] = 'image/vnd.microsoft.icon'



class WarpResourceWrapper(object):
    implements(IResource)

    isLeaf = False

    def __init__(self):
        self.warpBasePath = config['warpDir']
        self.warpStaticPath = self.warpBasePath.child('static')
        self.warpTemplatePath = self.warpBasePath.child("templates")

        siteTemplateDir = config['siteDir'].child("templates").path
        nodeTemplateDir = config['siteDir'].child("nodes").path    #NPK: the dir of the /nodes
        warpTemplateDir = self.warpTemplatePath.path
        templateLookup.__init__(directories=[siteTemplateDir, warpTemplateDir, nodeTemplateDir], output_encoding="utf-8")


        self.dispatch =  {
            '__login__': self.handle_login,
            '__logout__': self.handle_logout,
            '_comet': self.handle_comet,
            '_warp': self.handle_warpstatic,
            '': self.handle_default,
        }


    def getChildWithDefault(self, firstSegment, request):

        if firstSegment:
            fp = self.buildFilePath(request)
            if fp is not None:
                del request.postpath[:]
                return static.File(fp.path)

        # Init for everything except static files
        session = request.getSession()
        request.avatar = session.avatar

        if config.get('reloadMessages'):
            translate.loadMessages()

        request.translateTerm = translate.getTranslator(session.language)


        handler = self.dispatch.get(firstSegment)

        if handler is not None:
            return handler(request)

        node = helpers.getNode(firstSegment)

        if node is not None:
            if not access.allowed(request.avatar, node):
                return AccessDenied()
            return NodeResource(node)

        return NoResource()


    def putChild(self, path, child):
        self.dispatch[path] = lambda r: child


    def buildFilePath(self, request):
        filePath = config['siteDir'].child('static')
        for segment in request.path.split('/'):
            try: filePath = filePath.child(segment)
            except InsecurePath: return None

        if filePath.exists() and filePath.isfile():
            return filePath


    def handle_login(self, request):
        return auth.LoginHandler()

    def handle_logout(self, request):
        return auth.LogoutHandler()

    def handle_comet(self, request):
        return NodeResource(comet)

    def handle_warpstatic(self, request):
        filePath = self.warpStaticPath
        for segment in request.path.split('/')[2:]:
            try: filePath = filePath.child(segment)
            except InsecurePath: return None

        if filePath.exists() and filePath.isfile():
            del request.postpath[:]
            return static.File(filePath.path)

        return NoResource()

    def handle_default(self, request):
        return Redirect(config['default'])



class Redirect(object):
    implements(IResource)

    isLeaf = True

    def __init__(self, url):
        self.url = url

    def render(self, request):
        request.redirect(self.url)
        return "Redirecting..."



class AccessDenied(object):
    implements(IResource)

    isLeaf = True
    facetName = "view"
    args = ()

    def render(self, request):
        request.node = None
        request.resource = self
        template = templateLookup.get_template("/accessdenied.mak")
        return helpers.renderTemplateObj(request, template)



class NodeResource(object):
    implements(IResource)

    # You can always add a slash
    isLeaf = False


    def __init__(self, node):
        self.node = node
        self.facetName = None
        self.response = None
        self.args = []


    def getChildWithDefault(self, segment, request):

        if not segment:
            return Redirect(request.childLink('index'))

        renderFunc = self.getRenderFunc(segment)
        if renderFunc is not None:
            self.facetName = segment
            self.renderFunc = renderFunc
            self.isLeaf = True

            # Perform an additional check before rendering the response
            if not access.allowed(request.avatar, self.node, facetName=segment):
                return AccessDenied()
            response = self.getResponse(request)

            # Int is for NOT_DONE_YET. Maybe we should
            # check for a resource, rather than this?
            if isinstance(response, (str, int)):
                self.response = response
                return self
            else:
                return response

        subNode = self.getSubNode(segment)
        if subNode is not None:
            if not access.allowed(request.avatar, subNode):
                return AccessDenied()
            return NodeResource(subNode)

        return NoResource()


    def getResponse(self, request):
        self.args = [x for x in request.postpath if x]

        request.node = self.node
        request.resource = self

        return self.renderFunc(request)


    def render(self, request):

        if not self.facetName:
            request.redirect(request.childLink('index'))
            return "Redirecting..."

        # Should be configurable somehow
        request.setHeader("Pragma", "no-cache")
        request.setHeader("Expires", "-1")

        return self.response


    def getRenderFunc(self, facetName):

        renderFunc = getattr(self.node, 'render_%s' % facetName, None)
        if renderFunc is not None:
            return renderFunc

        templatePath = self.getTemplate(facetName)
        if templatePath is not None:
            return lambda r: helpers.renderTemplate(r, templatePath.path)

        renderer = getattr(self.node, 'renderer', None)
        if renderer is not None:
            renderMethod = getattr(renderer, 'render_%s' % facetName, None)
            if renderMethod is not None:
                return renderMethod

        return None


    def getTemplate(self, facetName):
        templatePath = FilePath(
            self.node.__file__
            ).sibling(facetName + ".mak")

        if templatePath.exists():
            return templatePath


    def getSubNode(self, nodeName):
        currentPackage = self.node.__name__.rsplit('.', 1)[0]
        try:
            return getattr(__import__("%s.%s" % (currentPackage, nodeName),
                                      fromlist=[nodeName]),
                           nodeName, None)
        except ImportError:
            return None


    def __repr__(self):
        return "<NodeResource: %s::%s (%s)>" % (
            self.node.__name__, self.facetName, self.args)
