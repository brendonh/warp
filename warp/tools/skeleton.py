import os

from twisted.python.filepath import FilePath

import warp


def createSkeleton(siteDir):
    fromDir = FilePath(warp.__file__).sibling("priv").child("skeleton")

    for entryName in (l.strip() for l in fromDir.child("MANIFEST").open()):
        entry = fromDir.preauthChild(entryName)

        destination = siteDir.preauthChild(entryName)

        if destination.exists():
            continue

        print "  Copying %s" % entryName

        if not destination.parent().exists():
            os.makedirs(destination.parent().path)

        entry.copyTo(destination)

    print "Done! Run with 'twistd -n warp'"
