/**
 * Created by PXke on 4/18/14.
 */

"use strict";
jQuery.ajaxSettings.traditional = true;

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


    $.getJSON("/harvester/log", {type: typesToPrint, limit: nbRow, module: document.getElementById("table_options").module.value},
        function (feedback) {

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
        );

}

function getNewLogs() {
    $.getJSON("/harvester/log", {datetime: lastDate, type: typesToPrint, limit: nbRow, module: document.getElementById("table_options").module.value},
        function (feedback) {
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
        );

    setTimeout(function () {getNewLogs(); }, 5000);
}
