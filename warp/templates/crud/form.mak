<%! from warp.helpers import link, button, url %>

<%

editing = facet in ('edit', 'create')

if editing:
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

  <tr>
    <th></th>
    <td colspan="2" class="warp-error generic-errors"></td>
  </tr>

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

</form>