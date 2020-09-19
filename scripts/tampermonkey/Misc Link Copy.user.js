// ==UserScript==
// @name         Misc Link Copy
// @namespace    http://tampermonkey.net/
// @version      0.1
// @require      http://code.jquery.com/jquery-3.3.1.slim.min.js
// @description  try to take over the world!
// @author       You
// @match        https://danbooru.donmai.us/*
// @match        https://www.pornhub.com/*
// @match        https://sukebei.nyaa.si/*
// @match        https://nyaa.si/*
// @match        https://horriblesubs.info/*
// @match        https://rule34.paheal.net/post/list/*
// @match        http://rule34.paheal.net/*
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
            if(key === 68) { // press d
                if (ret_val) {
                    document.getElementById("copy_status").textContent = " < Link Copy Mode [ON] > ";
                    ret_val = false;
                }
                else {
                    document.getElementById("copy_status").textContent = " < Link Copy Mode [OFF] > ";
                    ret_val = true;
                }
            }
        }, false);

        document.addEventListener('keydown',
            function(e) {
                var key = e.keyCode || e.which;
                if(key === 71) { // press g
                    if (!ret_val) {
                        event.preventDefault();
                        var copyText = document.getElementById("copy_list");
                        copyText.select();
                        document.execCommand("copy");
                        console.log("Id: copy_list [COPIED]");
                    }
                }
            }
        );

        $("a").click(function(event) {
            if (!ret_val) {
                event.preventDefault();
                copied_links++;
                var copied_href = $(this).attr("href");
                var t;
                if (!copied_href.startsWith("magnet:")) {
                    t = document.createTextNode(window.location.origin + copied_href + " ");
                }
                else {
                    t = document.createTextNode(copied_href + " ");
                }
                document.getElementById("copy_list").appendChild(t);
                document.getElementById("copy_status").textContent = " < Links Copied [" + copied_links + "] Click to Copy > ";
                //console.log(copied_href);
                //return ret_val;
            };
        });
    }
);