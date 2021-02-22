// ==UserScript==
// @name         Misc Link Copy
// @namespace    http://tampermonkey.net/
// @version      0.3
// @require      http://code.jquery.com/jquery-3.3.1.slim.min.js
// @description  try to take over the pork!
// @author       Me
// @match        https://danbooru.donmai.us/*
// @match        https://yande.re/*
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
        var ret_val = true; //Set OFF as default
        var linkHost = location.host;
        var linkPrefix = location.protocol + '//' + linkHost;
        console.log(linkHost);
        var codeMap = [68, 71, 70];
        var searchAll = null;
        var linkNext = null;
        if (linkHost.indexOf('booru') >= 0) {
            searchAll = 'article[id*="post_"]';
            linkNext = $("a#paginator-next").attr("href");
            // codeMap = [67, 86, 88]; // C V X
            codeMap = [68, 71, 70]; // D G F
        }
        else if (linkHost.indexOf('nyaa') >= 0) {
            searchAll = 'table[class*="torrent-list"] > tbody > tr.default > td.text-center';
            linkNext = $('ul.pagination > li > a[rel="next"]').attr("href");
            codeMap = [68, 71, 70]; // D G F
        }
        else if (linkHost.indexOf('pornhub') >= 0) {
            searchAll = '#mostRecentVideosSection, #videoCategory > li > .wrap > .phimage';
            linkNext = $("li.page_next.omega > a.orangeButton").attr("href");
            codeMap = [68, 71, 70]; // D G F
        }
        else {
            searchAll = 'article[id*="post_"]';
            linkNext = $("a#paginator-next").attr("href");
            codeMap = [68, 71, 70]; // D G F
        }

        var linkNow = location.search;
        var copyText = document.getElementById("copy_list");
        var copyStat = document.getElementById("copy_status");

        document.addEventListener('keydown', function(e) {
            var key = e.keyCode || e.which;
            if(e.shiftKey && key === codeMap[0]) { // D
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
            console.log('Function: NextPage Hotkey [Shift + ' + codeMap[1] + '] Un-Available');
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

        if (!searchAll) {
            console.log('Function: CopyAll Hotkey [Shift + ' + codeMap[2] + '] Un-Available');
        }
        else {
            document.addEventListener('keydown', function(e) {
                var key = e.keyCode || e.which;
                if (e.shiftKey && key === codeMap[2]) { // F
                    if (!ret_val) {
                        var all_posts = '### ' + linkNow + '\r\n';
                        $(searchAll).find('a').each( function() {
                            var x = $(this).attr("href");
                            if (x.indexOf('magnet') >= 0) {
                                all_posts += x + '\r\n';
                            }
                            else {
                                all_posts += linkPrefix + x + '\r\n';
                            }
                            copied_links++;
                        } );
                        var t = document.createTextNode(all_posts);
                        copyText.appendChild(t);
                        copyStat.textContent = " < Links Copied [" + copied_links + "] Click to Copy > ";
                        console.log("Copied: " + all_posts);
                    }
                }
            }, false);
        };
        $("a").click(function(event) {
            if (!ret_val) {
                event.preventDefault();
                copied_links++;
                var copied_href = $(this).attr("href");
                var t;
                if (!copied_href.startsWith("magnet:")) {
                    t = document.createTextNode(window.location.origin + copied_href + "\r\n");
                }
                else {
                    t = document.createTextNode(copied_href + "\r\n");
                }
                copyText.appendChild(t);
                copyStat.textContent = " < Links Copied [" + copied_links + "] Click to Copy > ";
                //console.log(copied_href);
                //return ret_val;
            };
        });
    }
);
