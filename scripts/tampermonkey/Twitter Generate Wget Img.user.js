// ==UserScript==
// @name         Twitter Generate Wget Img
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       Me
// @require      http://code.jquery.com/jquery-3.3.1.slim.min.js
// @match        https://twitter.com/*
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
        var post_user = location.href.split(location.host)[1].replace('/', '').split('/')[0];
        var ret_val = true; //Set OFF as default
        console.log(post_user);
        document.addEventListener('keydown', function(e) {
            var key = e.keyCode || e.which;
            if (key === 68) { //D key
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

        $("img").click(function(event) {
            if (!ret_val) {
                event.preventDefault();
                copied_links++;
                var img_rawsrc = $(this).attr("src")
                var img_elem = img_rawsrc.split('?');
                var url_split = img_elem[0].split('/');
                var img_name = url_split[url_split.length - 1];
                var img_format = img_elem[1].split('format=')[1].split('&')[0];
                var img_orig = img_elem[0] + '?format=' + img_format + '&name=orig';
                var copied_wget = 'wget --no-clobber "' + img_orig + '" -O "' + post_user + ' ' + img_name + '.' + img_format + '"';
                console.log(copied_wget);
                var t = document.createTextNode(copied_wget);
                var lnbr = document.createNode('br');
                document.getElementById("copy_list").appendChild(t);
                document.getElementById("copy_list").appendChild(lnbr);
                document.getElementById("copy_status").textContent = " < Links Copied [" + copied_links + "] Click to Copy > ";
                console.log("Copied: " + copied_wget);
                //return ret_val;
            }
            else {
                if ($(this).attr("href").indexOf('/show/') != -1) {
                    window.open($(this).attr("href"), '_blank');
                    focus();
                }
                else {
                    window.open($(this).attr("href"), '_self');
                };
           };
        });
    }
);
