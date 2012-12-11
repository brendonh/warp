<%! import json %>
<%! from warp.helpers import url, getCrudNode %>

<%
if model.listTitles:
   listTitles = [t for (c,t) in zip(model.listColumns, model.listTitles)
                 if c not in (exclude or [])]
else:
   listTitles = [c.title() for c in model.listColumns if c not in (exclude or [])]

colNames = list(listTitles)
if not model.hideListActions:
  colNames.append('Actions')

# This might not be the same as the request node, because
# this list gets embedded in other pages.
crudNode = getCrudNode(model)

if hasattr(request, 'gridCounter'):
   request.gridCounter += 1
else:
   request.gridCounter = 1

gc = request.gridCounter
createButtonID = "createButton%d" % gc
createBoxID = "createBox%d" % gc
listID = "list%d" % gc
%>

<script>

function delRow${listID}(id){
  $.post('${url(crudNode, "delete")}/' + id, function() {
     $("#${listID}").dataTable().fnDraw();
  });
};


$(document).ready(function(){ 

  $("#${listID}").dataTable({
    "sDom": "<'row-fluid'<'span6'l><'span6'f>r>t<'row-fluid'<'span6'i><'span6'p>>",
    "sPaginationType": "bootstrap",
    "bFilter": false,
    "bServerSide": true,
    "sAjaxSource": "${url(crudNode, 'list_json')}",
    "oLanguage": {
      "sLengthMenu": "_MENU_ records per page"
    },
    "aoColumnDefs": [
      % for i, c in enumerate(model.listColumns):
        <% 
           attrs = model.listAttrs.get(c)
           if attrs is None: continue
           attrs = attrs.copy()
           attrs['aTargets'] = [i]
        %>
        ${json.dumps(attrs)},
      % endfor
      % if not model.hideListActions:
      {
        "aTargets": [-1],
        "mData": 0,
        "mRender": function(id){
          return '<a href="#" class="label label-important" onclick="if(confirm(\'Delete?\')){delRow${listID}(' + id + ');} return false">Delete</a>';
        }
      }
      % endif
    ]
	});

});
</script>

<div class="warpCrud-list-container">

  <table cellpadding="0" cellspacing="0" border="0" class="table table-striped table-bordered" id="${listID}">
    <thead>
      <tr>
        % for c in colNames:
        <th>${c}</th>
        % endfor
      </tr>
    </thead>
    <tbody>
    </tbody>
  </table>

  % if allowCreate:
  <div style="margin-top: 10px">

    <button id="${createButtonID}" class="btn btn-primary pull-right" style="margin-bottom: 10px">Create New ${crudNode.renderer.model.__name__}</button>

    <div id="${createBoxID}" class="popupBox warpCrud"></div>
    
    <script type="text/javascript">
      jQuery(document).ready(function(){ 

        var fakeIDCounter = 1;
  
        var popupCreateBox = function() {
          $("#${createButtonID}").hide();
          $("#${createBoxID}").html("Loading...").show();
          $.get("${url(crudNode, "create")}?presets=${presets or '' | u}&noedit=${noEdit or '' | u}&fakeID="+fakeIDCounter, function(content) {
            $("#${createBoxID}").html(content).find("form").warpform(popupCreateDone);
  
          // Hack
          $("#${createBoxID}").find(".warpform-date").datepicker();
  
          });
          fakeIDCounter++;
        };
  
        var popupCreateDone = function(data) {
          console.log(data);
          var newID = data['results']['created'][0];
          var url = "${url(crudNode, 'view')}/" + newID;
          location.href = url;
        };

        $("#${createButtonID}").click(popupCreateBox);
      });
    </script>

  </div>
  % endif

</div>
