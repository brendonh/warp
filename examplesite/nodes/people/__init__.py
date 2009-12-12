from warp.runtime import store
from warp import helpers

from models import Person


def render_index(request):
    people = store.find(Person).order_by(Person.name)
    return helpers.renderLocalTemplate(request, "index.mak", 
                                       people=people)
