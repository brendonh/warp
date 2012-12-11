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
            return $.fn.warpform.submit(form, successCallback); });
        form.find(":input").removeAttr("disabled");
    };

    $.fn.warpform.setup = function() {
        $("form.warp").each(function() {
            $(this).warpform();
        });

        $("input.warp-autoclear").each(function() {

            var tag = this;
            var $tag = $(this);
            var origValue = $tag.val();
            var origColor = $tag.css("color");
            var origType = $tag.attr("type");

            $tag.css("color", "#999");
            tag.type = "text";

            $tag.focus(function() {
                tag.type = origType;
                $tag.css("color", origColor);
                if ($tag.val() == origValue) $tag.val("");
            });
        });

    };

    $.fn.warpform.submit = function(form, callback) {
        var subCount = $.fn.warpform.submissionCounter++;
        $.fn.warpform.uploadCallbacks[subCount] = {
            "_ids": []
        };

        try {

            // The bug here is that it doesn't check whether fields are already disabled,
            // and remember that fact if so.
            form.find(":input").attr("disabled", "disabled").removeClass("warp-error-highlight");
            form.find(".warp-error").empty();

            var objects = _collectForm(form, subCount);

            if ($.fn.warpform.uploadCallbacks[subCount]['_ids'].length) {
                _pendForm(form, objects, callback, subCount);
            } else {
                _sendForm(form, objects, callback);
            }

        } catch(e) {
            console.debug("Error submitting form: " + e);
        }
        return false;
    };



    $.fn.warpform.handleResponse = function(form, data, callback) {
        if (data['success']) {
            
            if (callback) {
                callback(data);
                return;
            } else if (form.attr("warp:redirect")) {
                document.location.href = form.attr("warp:redirect");
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



    // Upload-related stuff
    $.fn.warpform.submissionCounter = 0;
    $.fn.warpform.submissionCallbacks = {};

    $.fn.warpform.callbackCounter = 0;
    $.fn.warpform.uploadCallbacks = {};


    // Internal

    function _collectForm(form, subCount) {

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
                if (id[0] == 'n') {
                    obj['action'] = 'create';
                    id = id.substring(1);
                } else {
                    obj['action'] = 'update';
                }
                obj['id'] = id;
                objects[objKey] = obj;
            }

            var collectorName = _getCollectorName(el);
            $.fn.warpform.collectors[collectorName](
              key, el, field, obj['fields'], subCount);
        });
        
        var objList = [];
        for (key in objects) objList.push(objects[key]);

        return objList;
    };


    function _pendForm(form, objects, callback, subCount) {

        $.fn.warpform.submissionCallbacks[subCount] = function(id, fileID) {

            var uploadCallbacks = $.fn.warpform.uploadCallbacks[subCount];

            var fieldCallback = uploadCallbacks[id];

            if (fieldCallback) {

                fieldCallback(fileID);

                delete uploadCallbacks[subCount][id];

                for(var i=0; i<uploadCallbacks['_ids'].length; i++) {
                    if(uploadCallbacks['_ids'][i]==id)
                        uploadCallbacks['_ids'].splice(i,1); 
                } 

                // Submit if no pending callbacks remain
                if (!uploadCallbacks['_ids'].length) {
                    _sendForm(form, objects, callback);
                }
            }
        };
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
        if (!m) return null;
        return m[1];
    };

    function _getCollectorName(el) {
        var collector = "string";
        if (!el.attr("class")) return collector;
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

    function _uploadFile(k, el, f, obj, subCount) {
        var frame = window.frames[k];

        var document;
        if (frame.contentWindow) document = frame.contentWindow.document;
        else document = frame.document;

        if (!document) document = frame.contentWindow.document;

        var uploadForm = document.forms[0];            

        if (!(uploadForm && uploadForm["uploaded-file"].value)) {
            return;
        }

        var callbackID = $.fn.warpform.callbackCounter++;
        uploadForm['submitID'].value = subCount;
        uploadForm['callbackID'].value = callbackID;
        uploadForm.submit();
        $.fn.warpform.uploadCallbacks[subCount][callbackID] = function(value) {
            obj[f] = value;
        };
        $.fn.warpform.uploadCallbacks[subCount]['_ids'].push(callbackID);
    };


    // Field hooks
    
    $.fn.warpform.collectors = {
        "string": function(k, el, f, obj) { obj[f] = el.val(); },
        "date": _collectDate,
        "time": _collectTime,
        "bool": function(k, el, f, obj) { obj[f] = el.attr("checked") ? true : false; },
        "upload": _uploadFile,
        "stringset": function(k, el, f, obj) {
          if(!obj[f]) obj[f] = [];
          obj[f].push(el.val());
        },
        "checkset": function(k, el, f, obj) { 
          if (!obj[f]) obj[f] = []; 
          obj[f].push([el.val(), el.attr("checked") ? true : false]);
        },
        "radio": function(k, el, f, obj) { if (el.attr("checked")) obj[f] = el.val(); }
    };


})(jQuery);

jQuery(document).ready($.fn.warpform.setup);