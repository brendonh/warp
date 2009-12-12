<%inherit file="/site.mak"/>

<script type="text/javascript">

var startComet = function() {
    $.comet.init(
      function() {
        $.get("/demo/startCounter", {id: $.comet.id});
        $.comet("message", function(message) {
          $("#message").html("Counter set to: " + message['counter']);
        });
      });
}

$(document).ready(startComet);

</script>

<div id="message">Waiting for messages...</div>
        