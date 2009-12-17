<% from warp.helpers import link, button %>

<div class="warpCrud">
  <h1>${obj.model.__name__}: ${obj.name()}</h1>

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
      

  <table>
%for (col, colTitle) in zip(obj.crudColumns, obj.crudTitles or obj.crudColumns):
    <tr>
      <th>${colTitle}:</th>
      <td>${obj.renderView(col)}</td>
    </tr>
%endfor
  </table>

</div>