<%! from warp.helpers import link, button, url, getCrudObj, getCrudNode %>
<%! from warp.crud.model import CrudModel %>

<% 
crumbs = []
parent = crud
while parent is not None:
  crumbs.append(parent)
  pc = getattr(parent, 'parentCrumb', None)
  if pc is None: break
  parent = pc(request)
crumbs.reverse()
%>


<div class="warp-breadcrumbs">
% for i, crumb in enumerate(crumbs):
  <% linker = getattr(crumb, 'linkAsParent', None) %>
  <% if linker is None: continue %>
  % if i:
    &gt;
  % endif
  ${linker(request)}
% endfor
</div>

<div class="warpCrud">
  <h1>${crud.obj.__class__.__name__}: ${crud.name(request)}</h1>

  <div class="tabs">

% if crud.showListLink and not crud.parent(request):
    ${link("List", node)}
% endif

% for f in ('view', 'edit') + crud.extraFacets:

  % if f == facet:
    ${link(f.title(), node, f, args, class_="active")}

  % else:
    ${link(f.title(), node, f, args)}

  % endif
% endfor

    ${button("Delete", node, "delete", args, "Delete this item?")}
    <div style="clear: both"> </div>
  </div>

<%include file="${subTemplate}" />

</div>