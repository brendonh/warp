Installing Warp
===============


Debian / Ubuntu
---------------

Either download the latest Warp release from PyPI_ and install it in the normal way, or run the following:

.. _PyPI: http://pypi.python.org/pypi/warp

::

  sudo aptitude install python-dev python-setuptools
  sudo easy_install warp
  sudo python -c "from twisted.plugin import IPlugin, getPlugins; list(getPlugins(IPlugin))"

Now run ``twistd``, and if ``warp`` is listed in the commands, you're good to go.


Windows
-------

Install Python_, MinGW_, and Twisted_.

.. _Python: http://www.python.org/download/
.. _MinGW: http://www.mingw.org/wiki/HOWTO_Install_the_MinGW_GCC_Compiler_Suite
.. _Twisted: http://twistedmatrix.com/trac/wiki/Downloads

Add the MinGW path, the Python executable path, and the Python scripts path to your PATH environment variable (``Control Panel -> System -> Advanced -> Environment Variables``). Usually these are:

::

  c:\mingw\bin
  c:\Python26
  c:\Python26\scripts

Tell Python to use MinGW to build extension modules, by writing a file like ``c:\Python26\Lib\distutils\distutils.cfg`` containing:

:: 

  [build]
  compiler = mingw32

Then open ``cmd``, cross your fingers, and run:

::

  easy_install warp

Now run ``twistd``, and if ``warp`` is listed in the commands, you're good to go.
