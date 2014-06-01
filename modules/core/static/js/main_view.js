/**
 * Created by PXke on 4/18/14.
 */

"use strict";

var lastDate = "";
var nbRowInitial = 20;
var nbRow = nbRowInitial;
var typesToPrint = [];

function refresh() {
    typesToPrint = [];

    if (true === document.getElementById("table_options").option1.checked) {
        typesToPrint.push("TYPE_COMPLETE");
    }
    if (true === document.getElementById("table_options").option2.checked) {
        typesToPrint.push("TYPE_START");
    }
    if (true === document.getElementById("table_options").option3.checked) {
        typesToPrint.push("TYPE_INFO");
    }
    if (true === document.getElementById("table_options").option4.checked) {
        typesToPrint.push("TYPE_ERROR");
    }

    if (typesToPrint == []) {
        typesToPrint.push("TYPE_COMPLETE");
        typesToPrint.push("TYPE_START");
        typesToPrint.push("TYPE_INFO");
        typesToPrint.push("TYPE_ERROR");
    }
    nbRow = parseInt(document.getElementById("table_options").rows.value, 10);

    if (isNaN(nbRow)) {
        nbRow = nbRowInitial;
    }

    Ink.requireModules(['Ink.Net.Ajax_1'], function(Ajax) {
        var uri = '/harvester/log';
        new Ajax(uri,{
            method: 'GET',
            parameters:  {'type': typesToPrint, limit: nbRow, module: document.getElementById("table_options").module.value},
            onSuccess: function(xhrObj, req) {

                var feedback = JSON.parse(req);
                var myTbody = document.getElementsByTagName('tbody'), myContent = "";
                feedback.forEach(function (element) {

                    switch (element.type) {
                    case "TYPE_COMPLETE":
                        myContent += "<tr class='blue'>";
                        break;
                    case "TYPE_ERROR":
                        myContent += "<tr class='red'>";
                        break;
                    case "TYPE_START":
                        myContent += "<tr class='yellow'>";
                        break;
                    default:
                        myContent += "<tr>";
                        break;
                    }
                    myContent += "<td>" + new Date(element.datetime * 1000).toUTCString() + " </td><td> " + element.module + "</td><td>" + element.type + " </td><td>" + element.message + "</td></tr>";
                    if (lastDate <  element.datetime) {
                        lastDate =  element.datetime;
                    }
                });
                myTbody[0].innerHTML = myContent;

            }
        });
    });
}

function getNewLogs() {
       Ink.requireModules(['Ink.Net.Ajax_1'], function(Ajax) {
        var uri = '/harvester/log';
        new Ajax(uri,{
            method: 'GET',
            parameters:  {'type': typesToPrint, limit: nbRow, module: document.getElementById("table_options").module.value},
            onSuccess: function(xhrObj, req) {

                var feedback = JSON.parse(req);
                var myRows, myList = document.getElementsByTagName('tbody')[0], myContent = "";
                feedback.forEach(function (element) {
                    myRows = myList.childNodes;
                    myRows[myRows.length - 1].remove();
                    switch (element.type) {
                    case "TYPE_COMPLETE":
                        myContent += "<tr class='blue'>";
                        break;
                    case "TYPE_ERROR":
                        myContent += "<tr class='red'>";
                        break;
                    case "TYPE_START":
                        myContent += "<tr class='yellow'>";
                        break;
                    default:
                        myContent += "<tr>";
                        break;
                    }
                    myContent += "<td> " + new Date(element.datetime * 1000).toUTCString() + " </td><td> " + element.module + "</td><td>" + element.type + " </td><td>" + element.message + "</td></tr>";
                    if (lastDate <  element.datetime) {
                        lastDate =  element.datetime;
                    }

                });
                myList.innerHTML = myContent + myList.innerHTML;

            }
        });
    });
    setTimeout(function () {getNewLogs(); }, 5000);
}
