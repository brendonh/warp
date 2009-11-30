/*!
 * Jive Templating, v0.0.3
 * http://dev.brendonh.org:3854/
 *
 * Copyright (c) 2009 Brendon Hogger for Cogini
 * Licensed under the MIT license.
 *
 * Date: 2009-05-01
 * Revision: 4
 */


(function($) {

    $.expr.match.ATTR = /\[\s*((?:[:\w\u00c0-\uFFFF_-]|\\.)+)\s*(?:(\S?=)\s*(['"]*)(.*?)\3|)\s*\]/;

    $.fn.populate = function(json) {
        this.each(function() { 
            var tag = $(this);
            tag.jdata = json;
            try {
                $.fn.populate.handle(tag, json); 
            } catch(e) {
                console.debug("Oh noes: " + e);
            }
        });
        return this;
    };


    $.fn.populate.handle = function(tag, orig) {
        for (i in $.fn.populate.handlerOrder) {
            var attrName = $.fn.populate.handlerOrder[i];
            var attrVal = tag.attr(attrName);
            if (attrVal !== undefined) {
                tag = $.fn.populate.handlers[attrName](tag, attrVal, orig);
                tag.removeAttr(attrName);
            }
        }
        $.fn.populate.handleChildren(tag, orig);
        return tag;
    }
    

    $.fn.populate.handleChildren = function(tag, orig) {
        tag.children().each(function() {
          var child = $(this);
          child.jdata = tag.jdata;
          $.fn.populate.handle(child, orig);
        });
    };


    $.fn.populate.handlerOrder = ['j:key', 'j:slot', 'j:attr', 'j:render', 'j:callback'];

    $.fn.populate.handlers = {

        'j:key': function(tag, val, orig) {
            tag.jdata = tag.jdata[val];
            return tag;
        },

        'j:slot': function(tag, val, orig) {
            tag.html(tag.jdata[tag.attr("j:slot")].toString());
            return tag;
        },

        'j:attr': function(tag, val, orig) {
            var bits = val.split('|');
            tag.attr(bits[0], tag.jdata[bits[1]]);
            return tag;
        },

        'j:render': function(tag, val, orig) {
            if (val == "data") {
                tag.html(tag.jdata);
            } else if (val == "replace") {
                tag.replaceWith(tag.jdata);
            } else if (val == "foreach") {
                var content = tag.html();
                tag.empty();
                for(item in tag.jdata) {
                    var ph = $("<span>");
                    ph.jdata = tag.jdata[item];
                    ph.html(content);
                    $.fn.populate.handle(ph, orig);
                    tag.append(ph.html());
                }
            }
                
            return tag;
        },

        'j:callback': function(tag, val, orig) {
            var callback = tag.jdata[val];
            return callback(tag);
        },

    };


})(jQuery);