// ==UserScript==
// @name         E站主页下载按钮
// @namespace    http://tampermonkey.net/
// @version      2024-01-10
// @description  try to take over the world!
// @author       You
// @match        https://e-hentai.org/*
// @icon         https://e-hentai.org/favicon.ico
// @grant        GM_xmlhttpRequest
// @connect      192.168.1.3
// ==/UserScript==


function createStyleSheet(cssRules){

    var style = document.createElement('style');
    if(style.styleSheet){
        style.styleSheet.cssText = cssRules;
    }else{
        style.appendChild(document.createTextNode(cssRules));
    }
    document.getElementsByTagName('head')[0].appendChild(style);
}

(function() {
    'use strict';

    createStyleSheet(".myButton{width: 48px; height: 36px; font-size: 16px; cursor: pointer; border: none; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); border-radius: 6px; background-color: #b13c45; color:#fffde3; font-family:'微软雅黑';} .myButton:hover{background-color: #6b282d;} .myButton:active{background-color: #1f202d;}");
    var tdElements = document.querySelectorAll('td.gl3c.glname');

    for(var i = 0; i < tdElements.length; i++){
        var td = tdElements[i];
        var aElement = td.querySelector('a');
        var href = aElement.href;
        var myButton = document.createElement('button');

        myButton.className = "myButton"
        myButton.innerHTML = '下载';
        myButton.href = href;
        myButton.onmouseover = td.onmouseover;
        myButton.onmouseout = td.onmouseout;
        myButton.addEventListener('click', function() {
            // Your button click logic goes here
            // post local and download url

            console.log("try to download");
            var url_api = "http://192.168.1.3:8000/api/spider/ehentai";
            var url = this.href
            
            var xhr = GM_xmlhttpRequest({
                method: "post",
                url: url_api,
                data: JSON.stringify({ url : url }),
                headers: {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0",
                },
                onload: function(data) {
                    console.log(data);
                    data = JSON.parse(data.responseText);
                    console.log(data);
                    if( data.ret ){
                        alert("爬虫启动成功");
                    }else{
                        alert("爬虫启动失败 :" + data.msg);
                    }
                },
                onerror: function(data) {
                    alert("爬虫启动失败");
                },
                onabort: function(data) {
                    console.log("手动终止");
                }
            });
        });

        var myTd = document.createElement('td');
        myTd.appendChild(myButton);
        td.parentElement.insertBefore(myTd, td.nextElementSibling);
    }
})();