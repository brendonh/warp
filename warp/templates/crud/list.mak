<%! from warp.helpers import url %>
<%inherit file="/site.mak" />

<%
if model.listTitles:
   listTitles = model.listTitles
else:
   listTitles = [c.title() for c in model.listColumns]
%>

<script type="text/javascript">

jQuery(document).ready(function(){ 
  jQuery("#list").jqGrid({
    url:'list_json',
    datatype: 'json',
    mtype: 'GET',
    colNames:${list(listTitles)},
    colModel :[ 
<%
for c in model.listColumns:
    d = {'name': c, 'id': c}
    d.update(model.listAttrs.get(c, {}))
    context.write("%s," % repr(d))
%>
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
      $("#createBox").html(content).find("form").warpform();
    });
};


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
