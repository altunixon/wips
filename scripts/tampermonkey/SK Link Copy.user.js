// ==UserScript==
// @name         SK Link Copy
// @namespace    http://tampermonkey.net/
// @version      0.1
// @require      http://code.jquery.com/jquery-3.3.1.slim.min.js
// @description  tad janky but well... todo: fix onclick image, open background
// @author       Me
// @match        https://chan.sankakucomplex.com
// @match        https://idol.sankakucomplex.com
// @match        https://*.sankakucomplex.com/*?*tags*
// @grant        none
// ==/UserScript==

$(document).ready(
    function () {
        'use strict';
        var copy_element = '<style>textarea {width: 800px; height: 50px;}; th {color: Red; text-align: center; font-size: 15px;}</style>\
<center>\
<table width="640">\
<tr>\
<th onclick="copy_list()">[COPY]</td>\
<th id="copy_status" onclick="copy_list()"> < Copied List > </td>\
<th onclick="clear_list()">[CLEAR]</td>\
</tr>\
<tr>\
<td colspan="3"><textarea id="copy_list"></textarea></td>\
<tr>\
</table>\
</center>\
<script>\
function copy_list() {\
 var copyText = document.getElementById("copy_list");\
 copyText.select();\
 document.execCommand("copy");\
 document.getElementById("copy_status").textContent = " < List [COPIED] > "; \
}; \
function clear_list() {\
 document.getElementById("copy_list").textContent = "";\
 document.getElementById("copy_status").textContent = " < List [CLEARED] > "; \
};\
</script>';

        jQuery('body').prepend(copy_element);
        var copied_links = 0;
        var ret_val = true; //Set OFF as default
        document.addEventListener('keydown', function(e) {
            var key = e.keyCode || e.which;
            if (key === 68) {
                if (ret_val) {
                    document.getElementById("copy_status").textContent = " < Link Copy Mode [ON] > ";
                    ret_val = false;
                }
                else {
                    var copyText = document.getElementById("copy_list");
                    copyText.select();
                    document.execCommand("copy");
                    copyText.blur();
                    console.log("Id: copy_list [COPIED]");
                    document.getElementById("copy_status").textContent = " < Link Copy Mode [OFF] > ";
                    ret_val = true;
                }
            }
        }, false);

        $("a").click(function(event) {
            if (!ret_val) {
                event.preventDefault();
                copied_links++;
                var copied_href = 'https://chan.sankakucomplex.com' + $(this).attr("href") + '\r\n';
                var t = document.createTextNode(copied_href);
                document.getElementById("copy_list").appendChild(t);
                document.getElementById("copy_status").textContent = " < Links Copied [" + copied_links + "] Click to Copy > ";
                console.log("Copied: " + copied_href);
                //return ret_val;
            }
            else {
                if ($(this).attr("href").indexOf('/show/') != -1) {
                    window.open($(this).attr("href"), '_blank');
                }
                else {
                    window.open($(this).attr("href"), '_self');
                };
           };
        });
    }
);