<%! from warp.helpers import link, button, url %>

<div class="warpCrud">
  <h1>${obj.model.__name__}: ${obj.name(request)}</h1>

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

if redirect:
   redirectBit = ' warp:redirect="%s"' % redirect
else:
   redirectBit = ''

%>

<form class="warp" action="${url(node, 'save', args)}"${redirectBit}>

  <table>

<%
if obj.crudTitles:
  crudTitles = obj.crudTitles
else:
  crudTitles = [c.title() for c in obj.crudColumns]
%>

%for (col, colTitle) in zip(obj.crudColumns, crudTitles):
    <tr>
      <th>${colTitle}:</th>
      <td>${renderFunc(col, request)}</td>
      % if facet == 'edit':
      <td class="warp-error"></td>
      % endif
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