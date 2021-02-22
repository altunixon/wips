// ==UserScript==
// @name         SK Link Copy
// @namespace    http://tampermonkey.net/
// @version      0.3
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
<td colspan="3">\
<div id="tag_links" style="display: table-cell"></div>\
</td>\
</tr>\
<tr>\
<td colspan="3">Usage: Shift + (D)Toggle (G)Forward (F)GetAll</td>\
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
        var tagCombo = ["very_high_resolution", "high_resolution", "animated", "official_art", "paid_reward", "patreon_reward", "fanbox_reward", "fantia_reward", "gumroad_reward", "enty_reward", "extremely_large_filesize", "large_filesize", "video", "webm", "mp4"];
        var tagHilight = " very_high_resolution official_art paid_reward extremely_large_filesize video mp4";
        var ret_val = true; //Set OFF as default
        var linkPrefix = location.protocol + '//' + location.host;
        var linkNext = $("#paginator > div.pagination").attr("next-page-url");
        var linkNow = location.search;
        var codeMap = [68, 71, 70]; // D G F

        var copyText = document.getElementById("copy_list");
        var copyStat = document.getElementById("copy_status");

        document.addEventListener('keydown', function(e) {
            var key = e.keyCode || e.which;
            if (e.shiftKey && (key === codeMap[0] || key === 32)) { // Shift + D or Space
                if (ret_val) {
                    copyStat.textContent = " < Link Copy Mode [ON] > ";
                    ret_val = false;
                }
                else {
                    copyText.select();
                    document.execCommand("copy");
                    copyText.blur();
                    console.log("Id: copy_list [COPIED]");
                    copyStat.textContent = " < Link Copy Mode [OFF] > ";
                    ret_val = true;
                }
            }
        }, false);

        if (!linkNext) {
            console.log("Func: NextPage with [G] Disabled");
        }
        else {
            document.addEventListener('keydown', function(e) {
                var key = e.keyCode || e.which;
                if (e.shiftKey && key === codeMap[1]) { // G
                    copyText.select();
                    document.execCommand("copy");
                    copyText.blur();
                    if (linkNext != linkNow) {
                        window.open(linkNext, '_self')
                    }
                }
            }, false);
        };

        document.addEventListener('keydown', function(e) {
            var key = e.keyCode || e.which;
            if (e.shiftKey && key === codeMap[2]) { // F
                if (!ret_val) {
                    var all_posts = '### ' + linkNow + '\r\n';
                    $("div.content > div > span.thumb").find("a").each( function() {
                        all_posts += linkPrefix + $(this).attr("href") + '\r\n';
                        copied_links++;
                    } );
                    var t = document.createTextNode(all_posts);
                    copyText.appendChild(t);
                    copyStat.textContent = " < Links Copied [" + copied_links + "] Click to Copy > ";
                    console.log("Copied: " + all_posts);
                }
            }
        }, false);

        $("a").click(function(event) {
            if (!ret_val) {
                event.preventDefault();
                copied_links++;
                var copied_href = linkPrefix + $(this).attr("href") + '\r\n';
                var t = document.createTextNode(copied_href);
                copyText.appendChild(t);
                copyStat.textContent = " < Links Copied [" + copied_links + "] Click to Copy > ";
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

        if (linkNow.indexOf("tags=") >= 0) {
            var additiveTags = document.getElementById("tag_links");
            var sk_tagstart = linkNow.indexOf("tags=") + 5;
            if (linkNow.indexOf("%20", sk_tagstart) > 0) { sk_tagend = linkNow.indexOf("%20", sk_tagstart); }
            else if (linkNow.indexOf("&", sk_tagstart) > 0) { sk_tagend = linkNow.indexOf("&", sk_tagstart); }
            else { var sk_tagend = linkNow.length; }
            console.log("substr: " + sk_tagstart + '|' + linkNow.indexOf("%20", sk_tagstart) + '|' + linkNow.indexOf("&", sk_tagstart) + '|' + sk_tagend);
            var sk_maintag = linkNow.substr(sk_tagstart, sk_tagend - sk_tagstart);
            $.each( tagCombo, function( x, y ) {
                var z = sk_maintag + ' ' + y;
                var a = document.createElement('a');
                if (tagHilight.indexOf(' ' + y) >= 0) {a.style.color = 'red'};
                a.href = linkPrefix + '/?tags=' + z;
                a.text = ' /' + z + '/ ';
                additiveTags.appendChild(a);
            });
        };
    }
);
