<%! from warp.helpers import link, button, url %>

<%
if crud.crudTitles:
  crudTitles = crud.crudTitles
else:
  crudTitles = [c.title().replace('_', ' ') for c in crud.crudColumns]
%>

<table class="table">

% for (col, colTitle) in zip(crud.crudColumns, crudTitles):
  
  <%
  renderVal = crud.renderView(col, request)
  if renderVal is None:
    continue
  %>

  <tr>
    <td width="20%">
      % if colTitle:
      <strong>${colTitle}</strong>
      % endif
    </td>
    <td>
      ${renderVal}
    </td>
  </tr>
% endfor

</table>
