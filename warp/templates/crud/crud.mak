<% from warp.helpers import link, button, url %>

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
      
<%
if facet == 'edit':
    renderFunc = obj.renderEdit
else:
    renderFunc = obj.renderView
%>

<form action="${url(node, 'save', args)}" onsubmit="alert('Hah hah'); return false;">
  <table>
%for (col, colTitle) in zip(obj.crudColumns, obj.crudTitles or obj.crudColumns):
    <tr>
      <th>${colTitle}:</th>
      <td>${renderFunc(col)}</td>
    </tr>
%endfor

%if facet == 'edit':
    <tr>
      <td></td>
      <td><input type="submit" value="Save" /></td>
    </tr>
%endif

  </table>
</form>

</div>