/*!
 * Evo AMQP Bridge, v0.0.1
 *
 * Copyright (c) 2009 Brendon Hogger for Cogini
 * Licensed under the MIT license.
 *
 * Date: 2009-08-01
 * Revision: 1
 */

(function($) {

    $.amqp = function(routingKey, callback) {
        var timestamp = (new Date()).getTime();
        var queue = routingKey + timestamp;
        $.amqp.callbacks[routingKey] = callback;
        $.getJSON($.amqp.url, 
                  {"id": $.amqp.id, "queue": queue, "key": routingKey, "time": timestamp},
                  $.amqp.messages);
    };

    $.amqp.init = function(url, readyCallback) {
        $.amqp.url = url;
        $.amqp.callbacks = {};
        $.getJSON($.amqp.url + "/id", function(id) {
            $.amqp.id = id;
            if (readyCallback) { readyCallback(); }
        });
    };

    $.amqp.poll = function() {
        var timestamp = (new Date()).getTime();
        $.getJSON($.amqp.url, {"id": $.amqp.id, "time": timestamp}, $.amqp.messages);
    };

    $.amqp.messages = function(json) {
        $.each(json, function(i, obj) {
            var callback = $.amqp.callbacks[obj.key];
            if (callback) {
                try {callback(obj.key, obj.payload); }
                catch (e) { 
                    if (console && console.debug) {
                        console.debug("Oh noes: " + e);
                    }
                }
            }
        });
        $.amqp.poll();
    };

})(jQuery);