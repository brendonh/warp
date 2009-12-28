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

    $.fn.warpform = function(successCallback) {
        var form = $(this);
        form.bind("submit",  function(e) { 
            return $.fn.warpform.submit(form, successCallback) });
    };

    $.fn.warpform.setup = function() {
        $("form.warp").each(function() {
            $(this).warpform();
        });
    };

    $.fn.warpform.submit = function(form, callback) {
        try {

            // The bug here is that it doesn't check whether fields are already disabled,
            // and remember that fact if so.
            form.find(":input").attr("disabled", "disabled").removeClass("warp-error-highlight")
            form.find(".warp-error").empty();

            var objects = _collectForm(form);
            _sendForm(form, objects, callback);
        } catch(e) {
            console.debug("Error submitting form: " + e);
        }
        return false;
    };

    $.fn.warpform.handleResponse = function(form, data, callback) {
        console.dir(data);
        if (data['success']) {

            if (callback) {
                callback(data);
                return;
            } else {
                var redirect = form.attr("warp:redirect");
                if (redirect) document.location.href = redirect;
                return;
            }

        } else {
            for (var i in data['errors']) {
                var bits = data['errors'][i];
                var key = bits[0];
                var error = bits[1];

                if (key) {
                    var el = form.find(":input[name='warpform-" + key + "']");
                    el.addClass("warp-error-highlight");
                    el.parent().siblings(".warp-error").append(error + '<br />');
                } else {
                    form.find(".generic-errors").append(error + '<br />').show();
                }
            }
        }
        form.find(":input").removeAttr("disabled");
    };

    function _collectForm(form) {

        var objects = {};

        form.find(":input").each(function(i, tag) {
            var el = $(tag);
            var key = _getElementBits(el);
            if (!key) return;

            var keyParts = key.split('-');
            var model = keyParts[0];
            var id = keyParts[1];
            var field = keyParts[2];

            var objKey = model + '-' + id;
            var obj = objects[objKey];
            if (!obj) {
                obj = {'model': model, 'fields': {}};
                if (id[0] == '*') {
                    obj['action'] = 'create';
                    id = id.substring(1);
                } else {
                    obj['action'] = 'update';
                }
                obj['id'] = id;
                objects[objKey] = obj;
            }

            var collectorName = _getCollectorName(el);
            $.fn.warpform.collectors[collectorName](key, el, field, obj['fields']);
        });
        
        var objList = [];
        for (key in objects) objList.push(objects[key]);

        return objList;
    };
    
    function _sendForm(form, objects, callback) {
        $.ajax({
            "url": form.attr("action"),
            "type": "POST",
            "contentType": "application/json",
            "data": JSON.stringify(objects),
            "dataType": "json",
            "success": function(data, textStatus) {
                $.fn.warpform.handleResponse(form, data, callback);
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

    function _collectDate(k, el, f, obj) {
        if (!obj[f]) {
            obj[f] = [el.val(), 0];
            return;
        }
        obj[f][0] = el.val();
        obj[f] = _assembleDateTime(obj[f]);
    };

    function _collectTime(k, el, f, obj) {
        if (!obj[f]) {
            obj[f] = [0, el.val()];
            return;
        }
        obj[f][1] = el.val();
        obj[f] = _assembleDateTime(obj[f]);
    };

    function _assembleDateTime(dateAndTime) {
        return dateAndTime[0] + " " + dateAndTime[1];
    };

    $.fn.warpform.collectors = {
        "string": function(k, el, f, obj) { obj[f] = el.val(); },
        "date": _collectDate,
        "time": _collectTime,
        "bool": function(k, el, f, obj) { obj[f] = el.attr("checked") ? true : false; }
    };

})(jQuery);

jQuery(document).ready($.fn.warpform.setup);

