<%inherit file="/site.mak" />
<%! from warp.helpers import link, button, url, getCrudObj, getCrudNode %>

<%def name="contentHeader()">
  % if context.get('crud'):
    <h1>${crud.obj.__class__.__name__}: ${crud.name(request)}</h1>
  % else:
    <h1>${model.__warp_model__.__name__} List</h1>
  % endif

  % if context.get('crud'):
  <span class="facets">

    % if crud.showListLink and not crud.parentCrumb(request):
      ${link("List", node)}
    % endif

    % for f in ('view', 'edit') + crud.extraFacets:

      |

      % if f == facet:
        ${link(f.title(), node, f, args, class_="active")}

      % else:
        ${link(f.title(), node, f, args)}

      % endif
    % endfor

    | ${button("Delete", node, "delete", args, "Delete this item?")}
    <div style="clear: both"> </div>

  </span>
  % endif

</%def>

<%def name="breadCrumbs()">
  <% crumbs = [] %>

  % if context.get('crud'):
    <% 
    parent = crud
    while parent is not None:
      crumbs.append(parent)
      pc = getattr(parent, 'parentCrumb', None)
      if pc is None: break
      parent = pc(request)
    crumbs.reverse()
    %>
  % endif

  <% return crumbs %>
</%def>

<%include file="${subTemplate}" />
