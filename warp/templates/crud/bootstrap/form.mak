<%! from warp.helpers import link, button, url %>

<%
if redirect:
  redirectBit = ' warp:redirect="%s"' % redirect
else:
  redirectBit = ''
  
if crud.crudTitles:
  crudTitles = crud.crudTitles
else:
  crudTitles = [c.title().replace('_', ' ') for c in crud.crudColumns]
%>

<form class="warp form-horizontal" action="${url(node, 'save', args)}"${redirectBit}>
  <div class="warp-error generic-errors"></div>

% for (col, colTitle) in zip(crud.crudColumns, crudTitles):

  <%
  renderVal = crud.renderEdit(col, request)
  if renderVal is None:
    continue
  %>

  <div class="control-group">
    <label class="control-label" for="warp-${col}">
      % if colTitle:
        ${colTitle}:
      % endif
    </label>
    <div class="controls">
      <span>${renderVal}</span>
      <span class="help-inline"></span>
      <span class="warp-error"></span>
    </div>
  </div>

% endfor

  <div class="form-actions">
    <button type="submit" class="btn btn-primary">Save</button>
  </div>
</form>
