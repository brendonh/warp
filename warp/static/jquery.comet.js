/*!
 * Warp Comet Bridge, v0.0.1
 *
 * Copyright (c) 2009 Brendon Hogger for Cogini
 * Licensed under the MIT license.
 *
 * Date: 2009-11-30
 * Revision: 1
 */

(function($) {

    $.comet = function(key, callback) {
        var timestamp = (new Date()).getTime();
        $.comet.callbacks[key] = callback;
    };

    $.comet.init = function(readyCallback) {
        $.comet.callbacks = {};
        $.get("/_comet/id", function(id) {
            $.comet.id = id;
            if (readyCallback) { readyCallback(); }
            $.comet.poll();
        });
    };

    $.comet.poll = function() {
        var timestamp = (new Date()).getTime();
        $.getJSON("/_comet/longpoll", {"id": $.comet.id, "time": timestamp}, $.comet.messages);
    };

    $.comet.messages = function(json) {
        $.each(json, function(i, obj) {
            var callback = $.comet.callbacks[obj.key];
            if (callback) {
                try { callback(obj); }
                catch (e) { 
                    if (console && console.debug) {
                        console.debug("Oh noes: " + e);
                    }
                }
            }
        });
        $.comet.poll();
    };

})(jQuery);