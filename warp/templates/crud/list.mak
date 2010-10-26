<%! from warp.helpers import url, getCrudNode %>

<%
if model.listTitles:
   listTitles = [t for (c,t) in zip(model.listColumns, model.listTitles)
                 if c not in (exclude or [])]
else:
   listTitles = [c.title() for c in model.listColumns if c not in (exclude or [])]


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
pagerID = "pager%d" % gc

%>

<script type="text/javascript">

jQuery(document).ready(function(){ 

  function delLinkFormatter (cellvalue, options, rowObject) {
    return '[<a href="#" onclick="if (confirm(\'Delete?\')) { $.post(\'${url(crudNode, "delete")}/' + rowObject[0] + '\', {}, function() { $(\'#${listID}\').trigger(\'reloadGrid\'); }); }; return false" style="color: red">Del</a>]';
  }

  var grid = jQuery("#${listID}").jqGrid({
    url: '${url(crudNode, 'list_json')}',
    postData: ${postData or '{}'},
    datatype: 'json',
    mtype: 'GET',
    colNames:${list(listTitles) + ['Actions']},
    colModel :[ 
<%
for c in model.listColumns:
  if c in (exclude or []): continue
  d = {'name': c, 'id': c}
  d.update(model.listAttrs.get(c, {}))
  context.write("%s," % repr(d))
%>
    {'name': 'Actions', 'id': '_actions',
     'align': 'center', 'width': 50,
     'formatter':delLinkFormatter},
    ],
    pager: '#${pagerID}',
% for k, v in model.gridAttrs.iteritems():
  ${k}: ${v},
% endfor
  dummy: false
  }); 

}); 

</script>

<div class="warpCrud-list-container">

  <table id="${listID}"></table>
  <div id="${pagerID}"></div> 

  % if allowCreate:
  <div style="margin-top: 10px">

    <input type="button" value="Create New ${crudNode.renderer.model.__name__}"
           id="${createButtonID}" />

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
          $("#${listID}").trigger("reloadGrid");
          var form = $("#${createBoxID}").find("form");
          form.get(0).reset();
          form.find(":input").removeAttr("disabled");
          $("#${createBoxID}").hide();
          $("#${createButtonID}").show();
        };

        $("#${createButtonID}").click(popupCreateBox);
      });
    </script>

  </div>
  % endif

</div>