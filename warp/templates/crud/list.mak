<%! from warp.helpers import url %>
<%inherit file="/site.mak" />

<%
if model.listTitles:
   listTitles = model.listTitles
else:
   listTitles = [c.title() for c in model.listColumns]
%>

<script type="text/javascript">

var grid;


function delLinkFormatter (cellvalue, options, rowObject) {
  return '[<a href="javascript:deleteObj('+rowObject[0]+')" style="color: red">Del</a>]';
}


jQuery(document).ready(function(){ 
  grid = jQuery("#list").jqGrid({
    url:'list_json',
    datatype: 'json',
    mtype: 'GET',
    colNames:${list(listTitles) + ['Actions']},
    colModel :[ 
<%
for c in model.listColumns:
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
    viewrecords: true,
    caption: '${model.model.__name__} List'
  }); 
}); 

var popupCreateBox = function(button) {
    $(button).hide();
    $("#createBox").html("Loading...").show();
    $.get("${url(node, "create")}", function(content) {
      $("#createBox").html(content).find("form").warpform(popupCreateDone);
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
        $.post("${url(node, 'delete')}/" + id, {},
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
