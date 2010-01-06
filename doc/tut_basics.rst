Getting Started
===============


Create a site
-------------

Warp comes with a tool to set up a skeleton site structure. To use it, create an empty directory anywhere, and then run ``twistd warp skeleton`` inside it::

  mkdir mysite
  cd mysite
  twistd warp skeleton

Then run::

  twistd -n warp

You should now have a simple working warp site at http://localhost:8080.

If you want to know more about what just happened, see :ref:`somedetails`.


Change the homepage
-------------------

The ``Welcome to Warp..`` text you see on the homepage comes from a Mako_ template at::

  nodes/home/index.mak

.. _Mako: http://www.makotemplates.org/docs/

Open it up. The first line, ``<%inherit file="/site.mak"/>``, tells Mako to include the site template (see :ref:`below<edit-the-site-template>`). The rest 
is plain old HTML. Let's make it a little more interesting:

.. code-block:: mako

  <%inherit file="/site.mak"/>
 
  <h2>This is my site!</h2>

  <p>The current node is: ${node | h}</p>

  %if request.avatar:
    <p>You are logged in as: ${request.avatar.email}</p>
  %else:
    <p>You are not logged in.<p>
  %endif

  <p>Your IP address is: ${repr(request.channel.transport.getPeer().host)}</p>


Save the file and refresh the page, and you should get something like this::

  The current node is: <module 'nodes.home.home' from '/home/brendonh/temp/mysite/nodes/home/home.pyc'>
  You are not logged in.
  Your IP address is: '127.0.0.1'

Let's add an ``avatar`` to the database so we can log in.


Create a login avatar
---------------------

An ``avatar`` is an object representing a user. Any page can access the user's avatar, if they have one, as ``${request.avatar}``.
The Warp skeleton doesn't create any intially, so hit ctrl-c to stop your server, and let's make one. 

For now, that means some simple SQL::

  $ sqlite3 warp.sqlite
  sqlite> INSERT INTO warp_avatar (email, password) VALUES ('admin@mysite.com', 'sekrit');
  sqlite> .q

Now start your server again (``twistd -n warp``), and log in with those details. Now your home page
should show::

  You are logged in as: admin@mysite.com


Warp keeps its sessions in the DB automatically -- you can restart the server, and you will still be logged in.


Add another Mako page
---------------------

Warp will serve up any ``.mak`` file in a node directory as a page. So far we've been working with ``nodes/home/index.mak``, but let's create another page inside the ``home`` node::

  $ cat > nodes/home/about.mak
  <%inherit file="/site.mak"/>

  <h2>About This Site</h2>

  <p>This site is being created to showcase Warp.</p>

You can now access this page at http://localhost:8080/home/about. Let's add a link to it from the homepage, ``nodes/home/index.mak``:

.. code-block:: mako

  <%! from warp.helpers import link %>
  <p>${link("About this site", node, "about")}</p>

Of course, we could have just written ``<a href="about">About this site</a>``, but Warp's ``helpers`` module will be useful later.


.. _edit-the-site-template:

Edit the site template
----------------------

We should probably have a link to the ``About`` page in the navigation bar. Let's add one.

When you write ``<%inherit file="/site.mak"/>`` at the top of a page template, Warp looks it up in your ``templates`` directory. So, edit ``templates/site.mak``, find the section that looks like this:

.. code-block:: html

  <span class="links">
    <a href="/">Home</a>
  </span>

And change it to look like this:

.. code-block:: mako

  <%! from warp.helpers import link, getNode %>
  <span class="links">
    ${link("Home", getNode("home"))}
    ${link("About", getNode("home"), "about")}
  </span>

This time we couldn't just use ``node`` in the link, because this code will be used from other nodes too. So we use the ``getNode`` helper to find the ``home`` node, instead.

Let's make it a little more fancy, highlighting the current page:

.. code-block:: mako

  <%! from warp.helpers import link, getNode %>
 
  <%def name="navEntry(label, linkNode, linkFacet)">
    % if (linkNode, linkFacet) == (node, facet):
      <strong style="color: white;">${label}</strong> |
    % else:
      ${link(label, linkNode, linkFacet)} |
    % endif
  </%def>

  <span class="links">
  <% 
  for (label, nodeName, linkFacet) in (
     ("Home", "home", "index"), 
     ("About", "home", "about")):
        navEntry(label, getNode(nodeName), linkFacet)
  %>
  </span>

Here we're using some more Mako_ features -- function definitions, and ``for`` loops. We also have a new ``Warp`` word, ``facet``. Just as a ``node`` is a directory in your URLs, a ``facet`` is a page. So far, our two ``home`` facets (``index`` and ``about``) have been mako templates, but in the next section we'll write one which is pure Python.


A Pure-Python Facet
-------------------

Sometimes you want a ``facet`` that doesn't make sense as a Mako template. Perhaps it handles a POST, or uses Twisted's asynchronous magic (as we will here). Here's how.

Open ``nodes/home/home.py``, and add the following:

.. code-block:: python

  from twisted.internet import reactor
  from twisted.web.server import NOT_DONE_YET

  def render_delayed(request):
    
      def completeRequest():
          request.write("All done!")
          request.finish()

      reactor.callLater(5, completeRequest)

      return NOT_DONE_YET

Since this code is Python, rather than Mako, you'll need to restart your server (see :ref:`somedetails-caching`).

Now load http://localhost:8080/home/delayed. The server will wait for five seconds before loading the page. During those five seconds, it can still process other requests.


A New Node
----------

In the next chapter we're going to start playing with the database, using a ``people`` table. First, let's create a new node for our various ``people``-related pages::

  $ twistd warp node people
  Node 'people' created
  $

The ``node`` command creates a directory and a few files (``__init__.py``, ``people.py``, and ``index.mak``) in the site's ``nodes`` package. You should now be able to load http://localhost:8080/people, and see the index page.

We'll add it to the site navigation (in ``templates/site.mak``), too:

.. code-block:: mako

  <span class="links">
  <% 
  for (label, nodeName, linkFacet) in (
     ("Home", "home", "index"), 
     ("People", "people", "index"), 
     ("About", "home", "about")):
        navEntry(label, getNode(nodeName), linkFacet)
  %>
  </span>


Next: :doc:`tut_database`.
