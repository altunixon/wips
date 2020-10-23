// ==UserScript==
// @name         Exhg Gallery Pages Copy
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @require      http://code.jquery.com/jquery-3.3.1.slim.min.js
// @match        *://exhentai.org/g/*
// @match        *://e-hentai.org/g/*
// @grant        none
// ==/UserScript==

$(document).ready(
    function () {
        'use strict';
        var copy_status  = '<center><h4 id="copy_status1" onclick="copy_list()"> < Copied List > </h4></center>';
        var copy_element = '<style>textarea {width: 800px; height: 50px;}; th {color: Red; text-align: center; font-size: 15px;}</style>\
<center>\
<table width="640">\
<tr>\
<th onclick="copy_list()">[COPY]</th>\
<th id="copy_status2" onclick="copy_list()"> < Copied List > </th>\
<th onclick="clear_list()">[CLEAR]</th>\
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
 document.getElementById("copy_status2").textContent = " < List [COPIED] > "; \
}; \
function clear_list() {\
 document.getElementById("copy_list").textContent = "";\
 document.getElementById("copy_status2").textContent = " < List [CLEARED] > "; \
};\
</script>';

        jQuery('.gpc').prepend(copy_status);
        jQuery('#cdiv').prepend(copy_element);
        var copied_links = 0;
        var ret_val = true; //Set OFF as default
        /* https://www.cambiaresearch.com/articles/15/javascript-char-codes-key-codes */
        document.addEventListener('keydown', function(e) {
            var key = e.keyCode || e.which;
            // press d
            if(key === 68) {
                var text_field = document.getElementById("copy_list");
                if (ret_val) {
                    //$("a").css("pointer-events", "none");
                    console.log("Copy Mode [ON]");
                    document.getElementById("copy_status1").textContent = " < Copy Mode [ON] > ";
                    if ( ! text_field.innerHTML && ! window.location.href.includes("?p=") ) {
                        var h = document.createTextNode(window.location.href + ' pages=');
                        text_field.appendChild(h);
                    };
                    ret_val = false;
                }
                else {
                    text_field.select();
                    document.execCommand("copy");
                    text_field.blur();
                    console.log("Id: copy_list [COPIED]");
                    document.getElementById("copy_status1").textContent = " < Link Copy Mode [OFF] > ";
                    ret_val = true;
                }
            }
        }, false);

        $('td[onclick="document.location=this.firstChild.href"]').click(
            function(event) {
                if (!ret_val) {
                    event.preventDefault();
                    var copyText = document.getElementById("copy_list");
                    copyText.select();
                    document.execCommand("copy");
                    //window.location.href = this.href;
                    console.log("Id: copy_list [COPIED]");
                    //window.open(this.href, '_self');
                }
            }
        );

        document.addEventListener('keydown',
            function(e) {
                var key = e.keyCode || e.which; // press F
                if(key === 70) {
                    var pg_hsl = document.createTextNode('-');
                    document.getElementById("copy_list").appendChild(pg_hsl);
                }
            }
        );
        document.addEventListener('keydown',
            function(e) {
                var key = e.keyCode || e.which; // press E
                if(key === 82) {
                    var pg_hsl = document.createTextNode(',');
                    document.getElementById("copy_list").appendChild(pg_hsl);
                }
            }
        );
        document.addEventListener('keydown',
            function(e) {
                var key = e.keyCode || e.which; // press C
                if(key === 67) { clear_list(); }
            }
        );
        document.addEventListener('keydown',
            function(e) {
                var key = e.keyCode || e.which; // press G
                if(key === 71) { $('td[onclick="document.location=this.firstChild.href"]').click(); }
            }
        );

        $('a[href*="/s/"]').click(function(event) {
            if (!ret_val) {
                event.preventDefault();
                copied_links++;
                var copied_href = $(this).attr("href");
                //console.log(copied_href.split('-'));
                var text_field = document.getElementById("copy_list");
                var pg_num = copied_href.split('-', 2)[1];
                var pg_txt;
                if ( ! text_field.textContent || text_field.textContent.endsWith("pages=") ) {
                    if (event.ctrlKey) { pg_txt = '-' + pg_num; }
                    else { pg_txt = pg_num; }
                }
                else {
                    if (event.ctrlKey) { pg_txt = '-' + pg_num; }
                    else { pg_txt = ',' + pg_num; }
                }
                var pg_ele = document.createTextNode(pg_txt);
                document.getElementById("copy_list").appendChild(pg_ele);
                //console.log(document.getElementById("copy_list").textContent);
                document.getElementById("copy_status2").textContent = " < Page Copied [" + copied_links + "] Click to View > ";
                //console.log(copied_href);
                //return ret_val;
            }
        });
    }
);
