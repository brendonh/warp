from twisted.python import usage

class Options(usage.Options):
    """
    Create a new node
    """

    def parseArgs(self, name):
        self['name'] = name

    def postArgs(self):
        raise usage.UsageError("No node name given")

    def getSynopsis(self):
        return " node <name>"



def createNode(nodes, name, createIndex=True, nodeContent=""):

    segments = name.split('/')
    root = nodes
    
    for i, segment in enumerate(segments[:-1]):

        node = root.child(segment)
        if not node.exists():
            node.makedirs()
            node.child("__init__.py").open('w').write("")
            node.child("%s.py" % segment).open('w').write("""
def render_index(request):
  request.redirect("%s")
  return "Redirecting..."
""" % segments[i+1])

            print "Node '%s' created" % '/'.join(segments[:i+1])

        root = node

    nodeName = segments[-1]

    node = root.child(nodeName)
    node.makedirs()
    node.child("__init__.py").open('w').write("")
    node.child("%s.py" % nodeName).open('w').write(nodeContent)

    if createIndex:
        node.child("index.mak").open('w').write("""
<%%inherit file="/site.mak"/>

This is the index page for node '%s'.
""" % nodeName)

    print "Node '%s' created" % name
