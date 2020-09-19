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
        var post_done = new Array();
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

        $(document).on("click", "div.css-1dbjc4n", function () {
            if (!ret_val) {
                event.preventDefault();
                copied_links++;
                var img_rawsrc = $(this).find("img").attr("src")
                var img_elem = img_rawsrc.split('?');
                var url_split = img_elem[0].split('/');
                var img_name = url_split[url_split.length - 1];
                if (!post_done.includes(img_name)) {
                    var img_format = img_elem[1].split('format=')[1].split('&')[0];
                    var img_orig = img_elem[0] + '?format=' + img_format + '&name=orig';
                    var copied_wget = 'wget --no-clobber "' + img_orig + '" -O "' + post_user + ' ' + img_name + '.' + img_format + '"\\r\\n';
                    console.log(copied_wget);
                    var t = document.createTextNode(copied_wget);
                    // var lnbr = document.createElement('br');
                    document.getElementById("copy_list").appendChild(t);
                    // document.getElementById("copy_list").appendChild(lnbr);
                    document.getElementById("copy_status").textContent = " < Links Copied [" + copied_links + "] Click to Copy > ";
                    console.log("Copied: " + copied_wget);
                    //return ret_val;
                    post_done.push(img_name)
                }
                else {
                    console.log("Duplicate: " + img_rawsrc);
                };
                
            }
        });
    }
);
