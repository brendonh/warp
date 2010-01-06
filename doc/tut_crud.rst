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

The ``CrudModel`` is a proxy class for the real model (``Person``). It defines which fields to show in different pages (the ``listColumns`` and ``crudColumns`` attributes), some extra configuration for the Javascript grid used on the list page (``listAttrs``, which gets passed straight to jqGrid_), defines how to name the object in various places (``name()``), and overrides the default list rendering for the ``name`` column to add a link to the object's ``view`` page.

.. _jqGrid: http://www.trirand.com/blog/

Having written the ``CrudModel``, we then tell Warp we want to use it to expose the ``Person`` model, via ``expose``. This allows Warp to construct a ``CrudModel`` for any given Storm object, which it uses for form handling and other things.

Finally, we create a ``CrudRenderer`` object. If Warp finds an object called ``renderer`` in your node, it will call methods on it (like ``renderer.render_view(request)``) when there is no other renderer (a Mako template or ``render_`` function) for that facet. This is useful for implementing reusable node behaviours, like CRUD.

Note that we pass the Storm model, ``Person``, to the renderer, rather than the ``CrudModel``. Warp will find the ``CrudModel`` itself, thanks to the previous ``expose`` call.

