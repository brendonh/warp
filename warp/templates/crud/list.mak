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

%>

<script type="text/javascript">

var grid;


function delLinkFormatter (cellvalue, options, rowObject) {
  return '[<a href="javascript:deleteObj('+rowObject[0]+')" style="color: red">Del</a>]';
}


jQuery(document).ready(function(){ 
  grid = jQuery("#list").jqGrid({
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
    pager: '#pager',
    rowNum:10,
    rowList:[10,20,30],
    sortname: 'id',
    sortorder: 'asc',
    viewrecords: true
  }); 
}); 

var popupCreateBox = function(button) {
    $(button).hide();
    $("#createBox").html("Loading...").show();
    $.get("${url(crudNode, "create")}?presets=${presets or '' | u}&noedit=${noEdit or '' | u}", function(content) {
      $("#createBox").html(content).find("form").warpform(popupCreateDone);

      // Hack
      $("#createBox").find(".warpform-date").datepicker();

    });
};

var popupCreateDone = function(data) {
    $("#list").trigger("reloadGrid");
    var form = $("#createBox").find("form");
    form.get(0).reset();
    form.find(":input").removeAttr("disabled");
    $("#createBox").hide();
    $("#createButton").show();
};

var deleteObj = function(id) {
    if (confirm("Delete?")) {
        $.post("${url(crudNode, 'delete')}/" + id, {},
               function() { $("#list").trigger("reloadGrid"); });
    }
}

</script>

<div style="margin: 10px">

  <table id="list"></table>
  <div id="pager"></div> 

  <div style="margin-top: 10px">

    <input type="button" value="Create New" 
           id="createButton"
           onclick="popupCreateBox(this)" />

    <div id="createBox" class="popupBox warpCrud"></div>

  </div>

</div>
