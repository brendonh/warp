<%! from warp.helpers import link, button, url %>

<div class="warpCrud">
  <h1>${crud.obj.__class__.__name__}: ${crud.name(request)}</h1>

  <div class="tabs">
    ${link("List", node)}
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