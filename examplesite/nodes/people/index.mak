<%inherit file="/site.mak" />

<script type="text/javascript">

jQuery(document).ready(function(){ 
  jQuery("#list").jqGrid({
    url:'list_json',
    datatype: 'json',
    mtype: 'GET',
    colNames:${list(model.listTitles or model.listColumns)},
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

</script>

<div style="margin: 10px">
  <table id="list"></table>
  <div id="pager"></div> 
</div>

