<%inherit file="/site.mak" />

<script type="text/javascript">

jQuery(document).ready(function(){ 
  jQuery("#list").jqGrid({
    url:'list_json',
    datatype: 'json',
    mtype: 'GET',
    colNames:['ID', 'Name', 'Birthdate'],
    colModel :[ 
      {name:'id', index:'id', width:50, align:'center'}, 
      {name:'name', index:'name', width:200}, 
      {name:'birthdate', index:'birthdate', width:150, align:'center'}, 
    ],
    pager: '#pager',
    rowNum:10,
    rowList:[10,20,30],
    sortname: 'id',
    sortorder: 'asc',
    viewrecords: true,
    caption: 'People'
  }); 
}); 

</script>

<div style="margin: 10px">
  <table id="list"></table>
  <div id="pager"></div> 
</div>

