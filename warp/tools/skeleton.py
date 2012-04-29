import os

from twisted.python.filepath import FilePath
from twisted.python import usage

import warp


class Options(usage.Options):
    """ 
    Create a Warp site skeleton with the default layout
    """

    optParameters = (
        ("siteDir", "d", ".", "Base directory of the warp site"),
    )



def createSkeleton(siteDir):
    fromDir = FilePath(warp.__file__).sibling("priv").child("skeleton")

    for entryName in (l.strip() for l in fromDir.child("MANIFEST").open()):
        entry = fromDir.preauthChild(entryName)

        destination = siteDir.preauthChild(entryName)

        if destination.exists():
            continue

        print "  Copying %s" % entryName

        if not destination.parent().exists():
            destination.parent().makedirs()

        entry.copyTo(destination)

    print "Done! Run with 'twistd -n warp'"
