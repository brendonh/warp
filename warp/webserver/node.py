from twisted.python import modules

from warp.runtime import config



def findNodes():
    pp = modules.PythonPath([config['siteDir'].child('nodes').path])
    for entry in pp.walkModules():
        if not entry.isPackage():
            continue

        print "Node", entry, entry.filePath
