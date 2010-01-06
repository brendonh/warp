Forms and POST requests
=======================

Let's add a simple form for creating new people, at the bottom of ``nodes/people/index.mak``:

.. code-block:: mako

  [...]

  <hr />
  
  <%! from warp.helpers import url %>
  <p>
    Create a person: <br />
    <form method="post" action="${url(node, 'create')}">
      Name: <input type="text" name="name" /><br />
      Birthdate: <input type="text" name="birthdate" /> (YYYY-MM-DD)<br />
      <input type="submit" value="Create" />
    </form>
  </p>


The only new thing here is the ``url`` helper, which just spits out a URL for the given ``node`` and ``facet`` (and ``args``, if given).

Now we need to write the ``create`` facet, to actually create the person. We could of course just ``POST`` to the index page, and look for form values in the Mako template there. But that's a little messy, and can lead to bugs when a page is refreshed.

So instead, we'll write a pure Python facet to create the person, and then redirect the user to the new person's ``view`` facet.


A POST Handler Facet
--------------------

In ``nodes/people/people.py``, add:

.. code-block:: python

  from datetime import datetime
  from warp.runtime import store
  from warp.helpers import url
  from models import Person
  
  
  def render_create(request):
      name = request.args["name"][0].decode("utf-8")
      birthdateStr = request.args["birthdate"][0]
  
      year, month, day = birthdateStr.split('-')
      birthdate = datetime(int(year), int(month), int(day))
  
      person = Person()
      person.name = name
      person.birthdate = birthdate
      
      store.add(person)
      store.commit()
  
      request.redirect(url(request.node, "view", [person.id]))
  
      return "Redirecting..."


Now you should be able to fill in the form on the ``index`` page, and create a new ``Person``.


Error Handling
--------------

Let's add a little bit of (very lazy) error handling to that form processing code:

.. code-block:: python

  from datetime import datetime
  from warp.runtime import store
  from warp.helpers import url, renderLocalTemplate
  from models import Person
  
  
  def render_create(request):
  
      name = request.args["name"][0]
      birthdateStr = request.args["birthdate"][0]
  
      try:
          
          name = name.decode("utf-8")
  
          if not name:
              raise ValueError("You must provide a name.")
  
          year, month, day = birthdateStr.split('-')
          birthdate = datetime(int(year), int(month), int(day))
  
      except Exception, e:
          
          return renderLocalTemplate(request, "index.mak", 
                                     error=e,
                                     name=name, 
                                     birthdate=birthdateStr)
  
  
      person = Person()
      person.name = name
      person.birthdate = birthdate
      
      store.add(person)
      store.commit()
  
      request.redirect(url(request.node, "view", [person.id]))
      return "Redirecting..."
      

Here we just catch anything that goes wrong in the argument munging. Then we use Warp's ``renderLocalTemplate`` helper to re-render the index page. Note that we don't have to give it the built-in variables like ``node``, ``facet``, and ``store`` -- the helper adds those for you.

Back in ``nodes/people/index.mak``, we'll change the form to read like this:

.. code-block:: mako
  
  <hr />
  
  % if error:
    <div style="color: red; border: 1px solid red; padding: 5px">
      <strong>Error</strong>: ${error | h}
    </div>
  % endif
  
  <%! from warp.helpers import url %>
  <p>
    Create a person: <br />
    <form method="post" action="${url(node, 'create')}">
      Name: <input type="text" name="name" value="${name or ''}" /><br />
      Birthdate: <input type="text" name="birthdate" value="${birthdate or ''}" /> (YYYY-MM-DD)<br />
      <input type="submit" value="Create" />
    </form>
  </p>

This will display the error if there is one, and repopulate our two fields with whatever the user gave before.

Wasn't that boring? Fortunately, you don't actually have to write any of this for your regular CRUD -- Warp can help.

Next: :doc:`tut_crud`.
