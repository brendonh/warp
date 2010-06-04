<%! from warp.helpers import link, button, url, getCrudObj, getCrudNode %>

<% 
crumbs = []
parent = crud.obj
while parent is not None:
  parentCrud = getCrudObj(parent)
  crumbs.append(parentCrud)
  parent = parentCrud.parent(request)
crumbs.reverse()
%>


<div class="warp-breadcrumbs">
% for crumb in crumbs:
  &gt;
  ${link(crumb.name(request), getCrudNode(crumb), "view", [crumb.obj.id])} 
% endfor
</div>

<div class="warpCrud">
  <h1>${crud.obj.__class__.__name__}: ${crud.name(request)}</h1>

  <div class="tabs">

% if not crud.parent(request):
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