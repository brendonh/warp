Warp's CRUD Magic
=================

Let's create a new node, ``admin/people``, to put our People CRUD in::

  $ twistd warp node admin/people
  Node 'admin' created
  Node 'admin/people' created

This implicitly creates the ``admin`` node, making it redirect to ``admin/people``. Restart your server, and http://localhost:8080/admin should take you to the new page.


The CRUD Model
--------------

This time we don't actually want the ``index.mak`` that Warp created in ``nodes/admin/people/``, so **delete it**.

Now we're going to set up the CRUD model, which tells Warp how to build CRUD pages. Open ``nodes/admin/people/people.py``, and write:

.. code-block:: python

  from warp.crud.model import CrudModel
  from warp.crud.render import CrudRenderer
  from warp.helpers import link
  from warp.runtime import expose
  
  from models import Person
  
  class CrudPerson(CrudModel):
  
      listColumns = ("id", "name")
      crudColumns = ("name", "birthdate")
  
      listAttrs = {
          'id': {'width': 50, 'align': 'center'},
          'name': {'width': 200},
      }
  
      def name(self, request):
          return self.obj.name
  
      def render_list_name(self, request):
          return link(
              self.obj.name,
              request.node,
              "view", [self.obj.id])
  
  expose(Person, CrudPerson)

  renderer = CrudRenderer(Person)

Before we explain any of that, let's look at the result: http://localhost:8080/admin/people/. You now have a fairly complete CRUD interface for the Person class. It has some useful features built in, such as using a jQuery date picker on the edit page, and giving informative error messages for invalid values.

The code implementing all this is in two places -- the ``CrudModel`` and the ``CrudRenderer``.

``CrudPerson`` is a proxy class for the real model (``Person``). It defines which fields to show in different pages (the ``listColumns`` and ``crudColumns`` attributes), some extra configuration for the Javascript grid used on the list page (``listAttrs``, which gets passed straight to jqGrid_), defines how to name the object in various places (``name()``), and overrides the default list rendering for the ``name`` column to add a link to the object's ``view`` page.

.. _jqGrid: http://www.trirand.com/blog/

Having written the ``CrudModel``, we then tell Warp we want to use it to expose the ``Person`` model, via ``expose``. This allows Warp to construct a ``CrudModel`` for any given Storm object, which it uses for form handling and other things.

Finally, we create a ``CrudRenderer`` object. If Warp finds an object called ``renderer`` in your node, it will call methods on it (like ``renderer.render_view(request)``) when there is no other renderer (a Mako template or ``render_`` function) for that facet. This is useful for implementing reusable node behaviours, like CRUD.

Note that we pass the Storm model, ``Person``, to the renderer, rather than the ``CrudModel``. Warp will find the ``CrudModel`` itself, thanks to the previous ``expose`` call.


Warp Column Types
-----------------

Careful readers may have found a bug in the CRUD so far -- it allows the "Name" field to be empty.

To fix that, we're going to alter our original ``Person`` model, using one of Warp's custom column types:

.. code-block:: python
  
  import datetime
  from storm.locals import *
  from warp.crud import columns
  
  class Person(Storm):
      __storm_table__ = 'person'
  
      id = Int(primary=True)
      name = columns.NonEmptyUnicode(default=u'')
      birthdate = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))


``NonEmptyUnicode`` is a subclass of Storm's regular ``Unicode`` column type. It behaves exactly the same, but Warp maps it to a ``column proxy`` (see :ref:`below<column-proxies>`) which rejects empty values.

Restart your server and try to enter an empty name in a Person now -- you should get an informative error.

While we're at it, let's add some columns to ``person`` to demonstrate some other Warp column types::
  
  $ sqlite3 warp.sqlite
  SQLite version 3.5.9
  Enter ".help" for instructions
  sqlite> ALTER TABLE person ADD description TEXT NOT NULL DEFAULT '';
  sqlite> ALTER TABLE person ADD photo BLOB;
  sqlite> ALTER TABLE person ADD cash INTEGER NOT NULL DEFAULT 0;
  sqlite> .q
  
And update the Storm model:

.. code-block:: python

  import datetime
  from storm.locals import *
  from warp.crud import columns
  
  class Person(Storm):
      __storm_table__ = 'person'
  
      id = Int(primary=True)
      name = columns.NonEmptyUnicode(default=u'')
      birthdate = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))
      
      description = columns.Text(default=u'')
      photo = columns.Image()
      cash = columns.Price(default=0)

Finally, tell our ``CrudModel`` to include the new fields in view and edit pages:

.. code-block:: python

    [...]

    crudColumns = ("name", "birthdate", "photo", "description", "cash")
 
    [...]

Now your CRUD pages should have a textarea for ``description``, image upload and display for ``photo``, and a (rather poorly implemented) price widget for ``cash``.


Customizing Crud
----------------

There are two ways to customize the behaviour of a CRUD column. The first is to write one or more ``render_`` methods in the ``CrudModel``, and the second is to write a new ``column proxy`` that controls all the ways that column can be rendered.

We've already seen the first way, in ``CrudPerson``'s ``render_list_name`` method. Here it is again:

.. code-block:: python

  def render_list_name(self, request):
      return link(
          self.obj.name,
          request.node,
          "view", [self.obj.id])

This method is called whenever CRUD wants to render a ``Person.name`` field in a list page. We can write another method to render it in view pages:

.. code-block:: python

  def render_name(self, request):
      return '<span style="color: red">%s</span>' % self.obj.name

Now the name will be a nice bright red.

As well as ``render_*`` and ``render_list_*``, you can also write ``render_edit_*`` and ``save_*`` methods, but we'll skip right over those for now and talk about ``column proxies`` instead.


.. _column-proxies:

Column Proxies
--------------

Let's look at how Warp implements the price CRUD from earlier (``warp.crud.colproxy.PriceProxy``):

.. code-block:: python
  
  class PriceProxy(BaseProxy):
  
      def render_view(self, request):
          return "$%i.%.2i" % divmod(getattr(self.obj, self.col), 100)
  
      def render_edit(self, request):
          return '<input type="text" name="warpform-%s" value="%s" size="8" />' % (
              self.fieldName(),
              self.render_view(request))
  
      priceExp = re.compile(r'\$?([0-9]*)(?:\.([0-9]{2})|$)$')
  
      def save(self, val, request):
  
          m = self.priceExp.match(val)
  
          if not m:
              return u"'%s' is not a valid price" % val
  
          dollars, cents = m.groups()
  
          if not dollars: dollars = 0
          if not cents: cents = 0
  
          total = (int(dollars) * 100) + int(cents)
  
          setattr(self.obj, self.col, total)

The proxy has the same set of methods mentioned above -- ``render_view``, ``render_edit`` and ``save`` (There's no ``render_list_view`` here -- ``render_view`` is used instead). It has a couple of attributes, ``obj`` and ``col``, which let it access the original value. 

Finally, note that its ``save`` method is responsible for actually setting the new value on the object. However, it **must not call store.commit()**. This is so that Warp can attempt to save every field in a form, collect returned errors, and then commit the store only if there were none (rolling it back otherwise).

Let's write our own proxy class that contains very quiet text, rendering it in a tiny font and disallowing shouting. We'll put it in ``nodes/admin/people/people.py``, with our ``CrudPerson`` class:

.. code-block:: python
  
  from warp.crud import colproxy
  
  class QuietString(colproxy.StringProxy):
  
      def render_view(self, request):
          return u'<span style="font-size: 11px">%s</span>' % getattr(self.obj, self.col)
  
      def save(self, val, request):
          if all(c.isupper() or not c.isalpha() for c in val):
              return u"Please do not shout."
  
          setattr(self.obj, self.col, val)
  

We're staying away from ``render_edit`` for this example, since it needs more explanation.

For now, let's add a ``quote`` column to our person table::
  
  $ sqlite3 warp.sqlite
  sqlite> ALTER TABLE person ADD quote VARCHAR NOT NULL DEFAULT '';
  sqlite> .q

Add it to our Person model:

.. code-block:: python

  class Person(Storm):

      [...]

      quote = Unicode()

Finally, we add it to ``CrudPerson.crudColumns``, and tell it to use our new ``QuietString`` proxy:

.. code-block:: python

  class CrudPerson(CrudModel):

    [...]

    crudColumns = ("name", "birthdate", "photo", "description", "cash", "quote")

    [...]

    def render_proxy_quote(self, request):
        return QuietString(self.obj, "quote")

Now restart the server, and the ``quote`` field should be working. Enter "HELLO WORLD" and it will ask you not to shout. Enter something quieter, and it will accept it, and render it tiny.

