/*!
 * Warp Form Stuff, v0.0.1
 *
 * Copyright (c) 2009 Brendon Hogger for Cogini
 * Licensed under the MIT license.
 *
 * Date: 2009-12-25
 * Revision: 1
 */

(function($) {

    $.fn.warpform = function() {
        var form = $(this);
        form.bind("submit",  $.fn.warpform.submit);
    };

    $.fn.warpform.setup = function() {
        $("form.warp").each(function() {
            $(this).warpform();
        });
    };

    $.fn.warpform.submit = function() {
        var form = $(this);
        try {
            var bits = _collectForm(form);
            _sendForm(form, bits);
        } catch(e) {
            console.debug("Error submitting form: " + e);
        }
        return false;
    };

    $.fn.warpform.handleResponse = function(form, data) {
        console.debug("Response for " + form);
        console.dir(data);
    };

    function _collectForm(form) {
        var bits = {};
        form.find(":input").each(function(i, tag) {
            var el = $(tag);
            var key = _getElementBits(el);
            if (!key) return;
            var collectorName = _getCollectorName(el);
            $.fn.warpform.collectors[collectorName](key, el, bits);
        });
        return bits;
    }
    
    function _sendForm(form, bits) {
        $.ajax({
            "url": form.attr("action"),
            "type": "POST",
            "contentType": "application/json",
            "data": JSON.stringify(bits),
            "dataType": "json",
            "success": function(data, textStatus) {
                $.fn.warpform.handleResponse(form, data);
            },
            "error": function (XMLHttpRequest, textStatus, errorThrown) {
                console.debug("Error: " + textStatus);
            }
        });
    };

    function _getElementBits(el) {
        var m = /^warpform-(.+)$/.exec(el.attr("name"));
        if (!m) return;
        return m[1];
    };

    function _getCollectorName(el) {
        var collector = "string";
        var classes = el.attr("class").split(/\s+/);
        for (var i in classes) {
            var m = /^warpform-(.+)$/.exec(classes[i]);
            if (m) {
                collector = m[1];
                break;
            }
        }
        return collector;
    };

    function _collectDate(k, el, bits) {
        if (!bits[k]) {
            bits[k] = [el.val(), 0];
            return;
        }
        bits[k][0] = el.val();
        bits[k] = _assembleDateTime(bits[k]);
    };

    function _collectTime(k, el, bits) {
        if (!bits[k]) {
            bits[k] = [0, el.val()];
            return;
        }
        bits[k][1] = el.val();
        bits[k] = _assembleDateTime(bits[k]);
    };

    function _assembleDateTime(dateAndTime) {
        return dateAndTime[0] + " " + dateAndTime[1];
    }

    $.fn.warpform.collectors = {
        "string": function(k, el, bits) { bits[k] = el.val(); },
        "date": _collectDate,
        "time": _collectTime,
        "bool": function(k, el, bits) { bits[k] = el.attr("checked") ? true : false; }
    }

})(jQuery);

jQuery(document).ready($.fn.warpform.setup);