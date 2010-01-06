.. _somedetails:

Some Details
============

The Warp directory structure
----------------------------

When you ran the ``skeleton`` tool, it created a file structure something like this:

::

  warpconfig.py         (Configuration for your site)
                   
  nodes/                (Directories in your site's URLs)
    __init__.py

    home/               (One such directory)
      __init__.py  
      home.py       
      index.mak         (The template for your home page)

  static/               (Static files like images, JS, and CSS)
    favicon.ico         

    css/           
      site.css     

  templates/            (General templates, like site templates,
    site.mak             or includes used in multiple places)


We'll look at each of these parts in turn below.


Site Configuration
------------------

The ``warpconfig.py`` file is special -- warp looks for it when it starts up. It should contain a dictionary called ``config``, which in the skeleton looks something like this:

::

  config = {
    'domain': 'localhost',          (Currently unused, may be used to build links in the future)
    'port': 8080,                   (The port twisted makes your site available on)
    'db': 'sqlite:warp.sqlite',     (Any DB connection string supported by Storm)
    'default': 'home',              (The default node)
  }

Setting ``'home'`` as the default node means that when a user visits http://localhost:8080, they will be redirected to http://localhost:8080/home/index/.


.. _somedetails-caching:

Caching
-------

One reason ``node`` files usually contain functions, rather than objects, is to encourage writing responders in a functional style. This will (later) allow Warp to reload them safely. Some files, like Storm model definitions, will always require a server restart on change, but most files should be safely reloadable. 

Eventually, Warp will have ``production`` and ``development`` modes. In ``production`` mode, Warp will never reload anything, unless specifically told (by means as yet unknown) to flush its cache. In ``development`` mode, it will reload everything in ``nodes``.
