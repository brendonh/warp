from twisted.python import usage

COMMAND_MODULES = (
  "skeleton",
  "node",
  "autocrud",
  "console",
  "command",
  "adduser",
)

# from warp.tools import (
#     skeleton, node, autocrud, console, command, adduser
#     )

class Options(usage.Options):
    subCommands = []

    def getSynopsis(self, width=None):
        return ""


def run():
    for moduleName in COMMAND_MODULES:
        module = __import__("warp.tools.%s" % moduleName, fromlist=[moduleName])
        description = getattr(module.Options, '__doc__') or ''
        Options.subCommands.append(
            (moduleName, None, module.Options, description.strip()))

    Options.subCommands.sort()

    config = Options()

    try:
        config.parseOptions()
    except usage.UsageError:
        if hasattr(config, 'subOptions'):
            print "Usage: warp%s\n\n%s" % (config.subOptions.getSynopsis(),
                                           config.subOptions.getUsage())
            return

    if not config.subCommand:
        print config
        return

    print "Command:", config.subCommand


if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, '/home/brendonh/projects/warp')
    run()






# class Options(usage.Options):
#     optParameters = (
#         ("siteDir", "d", ".", "Base directory of the warp site"),
#     )

#     subCommands = (
#         ("skeleton", None, SkeletonOptions, "Copy Warp site skeleton into current directory"),
#         ("node", None, NodeOptions, "Create a new node"),
#         ("crud", None, CrudOptions, "Create a new CRUD node"),
#         ("adduser", None, usage.Options, "Add a user (interactive)"),
#         ("console", None, usage.Options, "Python console with Warp runtime available"),
#         ("command", "c", CommandOptions, "Run a site-specific command"),
#     )
