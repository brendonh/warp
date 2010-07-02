<%! from warp.helpers import link, button, url %>

<%

editing = facet in ('edit', 'create')

if editing:
  renderFunc = crud.renderEdit
else:
  renderFunc = crud.renderView

if redirect:
  redirectBit = ' warp:redirect="%s"' % redirect
else:
  redirectBit = ''

%>

% if editing:
<form class="warp" action="${url(node, 'save', args)}"${redirectBit}>
% endif

  <table>

  <tr>
    <th></th>
    <td colspan="2" class="warp-error generic-errors"></td>
  </tr>

<%
if crud.crudTitles:
  crudTitles = crud.crudTitles
else:
  crudTitles = [c.title() for c in crud.crudColumns]
%>

%for (col, colTitle) in zip(crud.crudColumns, crudTitles):

<%
renderVal = renderFunc(col, request)
if renderVal is None:
  continue
%>

    <tr>
      <th>${colTitle}:</th>
      <td>${renderVal}</td>
      % if editing:
      <td class="warp-error"></td>
      % endif
    </tr>
%endfor

%if editing:
    <tr>
      <td></td>
      <td><input type="submit" value="Save" /></td>
    </tr>
%endif

  </table>

% if editing:
</form>
% endif