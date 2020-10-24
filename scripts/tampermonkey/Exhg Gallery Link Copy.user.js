// ==UserScript==
// @name         Exhg Gallery Link Copy
// @namespace    http://tampermonkey.net/
// @version      0.2
// @require      http://code.jquery.com/jquery-3.3.1.slim.min.js
// @description  try to take over the pork!
// @author       You
// @match        https://exhentai.org
// @match        https://exhentai.org/?*
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

        jQuery('.dp > a:contains("Front Page")').parent().before(copy_element);
        var copied_links = 0;
        var ret_val = true; //Set OFF as default

        document.addEventListener('keydown', function(e) {
            var key = e.keyCode || e.which;
            if(key === 68) { // D
                if (ret_val) {
                    //$("a").css("pointer-events", "none");
                    //console.log("Link Copy Mode [ON]");
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

        document.addEventListener('keydown',
            function(e) {
                var key = e.keyCode || e.which;
                if(key === 71) { // press G
                    var text_field = document.getElementById("copy_list");
                    text_field.select();
                    document.execCommand("copy");
                    text_field.blur();
                    $("td[onclick='document.location=this.firstChild.href']:contains('>')").click();
                }
            }
        );

        document.addEventListener('keydown',
            function(e) {
                var key = e.keyCode || e.which;
                if(key === 65) { // press A
                    var text_field = document.getElementById("copy_list");
                    text_field.select();
                    document.execCommand("copy");
                    text_field.blur();
                    $("td[onclick='document.location=this.firstChild.href']:contains('<')").click();
                }
            }
        );

        $("a").click(function(event) {
            if (!ret_val) {
                event.preventDefault();
                copied_links++;
                var copied_href = $(this).attr("href");
                var t = document.createTextNode("'" + copied_href + "' ");
                document.getElementById("copy_list").appendChild(t);
                document.getElementById("copy_status").textContent = " < Links Copied [" + copied_links + "] Click to Copy > ";
                //console.log(copied_href);
                //return ret_val;
            };
        });
    }
);
