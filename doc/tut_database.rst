Using The Database
==================

Let's set up a simple table for people.

.. code-block:: sql

  $ sqlite3 warp.sqlite
  SQLite version 3.5.9
  Enter ".help" for instructions
  sqlite> CREATE TABLE person (
     ...>   id INTEGER NOT NULL PRIMARY KEY,
     ...>   name VARCHAR NOT NULL,
     ...>   birthdate VARCHAR
     ...> );
  sqlite> .q


Defining and Using Storm Models
-------------------------------

Warp doesn't care where you define your ORM models, but it should be outside your nodes (since those may be reloaded at runtime -- see :ref:`somedetails-caching`). We'll put ours straight in the ``mysite`` directory, in ``models.py``.

.. code-block:: python

  import datetime
  from storm.locals import *

  class Person(Storm):
      __storm_table__ = 'person'

      id = Int(primary=True)
      name = Unicode(default=u'')
      birthdate = DateTime(default_factory = lambda: datetime.datetime(1970, 1, 1))


And then we'll write some view code in ``nodes/people/index.mak``:

.. code-block:: mako

  <%inherit file="/site.mak"/>
  
  <%
  from models import Person
  
  people = store.find(Person)
  
  total = people.count()
  %>
  
  <p>There are ${total} people in the database:</p>
  
  % for person in people:
    <p>
      ${person.name}, born on ${person.birthdate.strftime("%x")}
    </p>
  % endfor
    
Now restart the server (to make sure ``models.py`` gets reloaded), and http://localhost:8080/people/index should show::

  There are 0 people in the database:


Let's add a person. We can do this through the Warp ``console`` command, which sets up Warp's runtime (e.g. the ``store``) and then drops you into a Python console:

.. code-block:: pycon
  
  $ twistd warp console
  Python 2.5.2 (r252:60911, Oct  5 2008, 19:24:49) 
  [GCC 4.3.2] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  (InteractiveConsole)
  >>> import datetime
  >>> from models import Person
  >>> brend = Person(); brend.name = u"Brendon"; brend.birthdate = datetime.datetime(1981, 8, 15)
  >>> store.add(brend)
  <models.Person object at 0xa45c64c>
  >>> store.commit()


Now reload http://localhost:8080/people/index and you should see::

  There are 1 people in the database:

  Brendon, born on 08/15/81


A Simple View Page
------------------

Let's give each person their own page with their details. We'll put it in the ``people`` node's ``view`` facet, i.e. ``nodes/people/view.mak``:

.. code-block:: mako

  <%inherit file="/site.mak"/>
  
  <%
  from models import Person
  
  id = int(request.resource.args[0])
  person = store.get(Person, id)
  %>
  
  <h1>${person.name}</h1>
  
  <p>Date of Birth: ${person.birthdate.strftime("%x")}</p>

There's just one new feature here: ``request.resource.args``. This is a list of URL segments after the ``node`` and ``facet``. So http://localhost:8080/people/view/1 will have ``["1"]`` in its args. Loading it, you should see::

  Brendon
  Date of Birth: 08/15/81


Finally, we'll change our list code in ``nodes/people/index.mak`` to link each person to their view page:

.. code-block:: mako

  <%! from warp.helpers import link %>
  % for person in people:
    <p>
      ${link(person.name, node, "view", [person.id])}
    </p>
  % endfor


Next: :doc:`tut_forms`.
