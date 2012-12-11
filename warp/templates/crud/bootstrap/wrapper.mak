<%inherit file="/site.mak" />
<%! from warp.helpers import link, button, url, getCrudObj, getCrudNode %>

<%def name="contentHeader()">
  % if context.get('crud'):
    <h1>${crud.obj.__class__.__name__}: ${crud.name(request)}</h1>
  % else:
    <h1>${model.__warp_model__.__name__} List</h1>
  % endif

  % if context.get('crud'):
    <div class="btn-group" style="margin-right:15px">
    % for f in ('view', 'edit') + crud.extraFacets:
      % if f == facet:
        ${link(f.title(), node, f, args, class_="btn disabled")}
      % else:
        ${link(f.title(), node, f, args, class_="btn")}
      % endif
    % endfor
    </div>
    ${button("Delete", node, "delete", args, "Delete this item?", class_="btn btn-danger")}
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
