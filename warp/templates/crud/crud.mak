<%! from warp.helpers import link, button, url, getCrudObj, getCrudNode %>
<%! from warp.crud.model import CrudModel %>

<% 
crumbs = []
parent = crud
while parent is not None:
  crumbs.append(parent)
  parent = parent.parentCrumb(request)
crumbs.reverse()
%>


<div class="warp-breadcrumbs">
% for i, crumb in enumerate(crumbs):
  % if i:
    &gt;
  % endif
  ${crumb.linkAsParent(request)}
% endfor
</div>

<div class="warpCrud">
  <h1>${crud.obj.__class__.__name__}: ${crud.name(request)}</h1>

  <div class="tabs">

% if crud.showListLink and not crud.parent(request):
    ${link("List", node)}
% endif

% for f in ('view', 'edit'):

  % if f == facet:
    ${link(f.title(), node, f, args, class_="active")}

  % else:
    ${link(f.title(), node, f, args)}

  % endif
% endfor

    ${button("Delete", node, "delete", args, "Delete this item?")}
    <div style="clear: both"> </div>
  </div>
      
<%include file="form.mak" />

</div>