/**
 * Created by PXke on 4/18/14.
 */
"use strict"

var lastRefreshDate = 0, a, newRow;

function getNameCell(innerHTML) {
    var temp = innerHTML.substring(innerHTML.indexOf("name=") + 6);
    return temp.substring(0, temp.indexOf("\""));
}


function updateFields(name, value) {
    var z, i, x, row = document.getElementById(name + "-row");
    for (i = 0; i < a.length; i = i + 1) {
        if (a[i][0] === value) {
            for (z = row.cells.length - 1; z > -1; z = z - 1) {
                if (!getNameCell(row.cells[z].innerHTML).match("^send$|^delete$|^name$|^harvesting_function$")) {
                    row.deleteCell(z);
                }
            }

            for (z = 0; z < a[i][1].length; z = z + 1) {
                if (name === "new") {
                    x = row.insertCell(row.cells.length - 1);
                } else {
                    x = row.insertCell(row.cells.length - 2);
                }
                x.innerHTML = "<div class='control-group'><label'> " + a[i][1][z] + " :</label><div class='control'><input type='text' name=" +  a[i][1][z] + " value=''></div>";
            }
            break;
        }
    }
}

function createNewRow(parameters, table) {
    var newRowCode = "", projetToComplete, mem, harvest_function, z;
    newRowCode = "<form id='" + parameters._id + "' class='ink-form'>";
    newRowCode += "<table class='ink-table bordered vertical-space'>";
    newRowCode += "<tr id='" + parameters._id + "-row'>";
    newRowCode += "<td> <div class='control-group'><label>Name :</label> <div class='control'><input type='text' name='name' value='" + parameters.name + "'> </div></div></td>";
    newRowCode += "<td> <div class='control-group'><label>Harvesting function :</label><div class='control'>";
    newRowCode += "<select id='" + parameters._id + "-select' onchange='updateFields(\"" + parameters._id + "\", this.value);' name='harvesting_function' >";

    for (harvest_function in a) {
        if (a[harvest_function][0] === parameters.harvesting_function) {
            newRowCode += "<option value='" + a[harvest_function][0] + "'>" + a[harvest_function][0] + "</option>";
            mem = harvest_function;
        } else {
            newRowCode += "<option value=" + a[harvest_function][0] + ">" + a[harvest_function][0] + "</option>";
        }
    }
    newRowCode += "</select></div></div></td>";
    newRowCode += "<td><input onclick='deleteProject(\"" + parameters._id + "\");' type='button' name='delete' value='Delete'></td>";
    newRowCode += "<td><input onclick='sendProject(\"" + parameters._id + "\");' type='button' name='send' value='Send'></td>";
    newRowCode += "</tr>";
    newRowCode += "</table>";
    newRowCode += "</form>";
    table.innerHTML =  table.innerHTML + newRowCode;
    updateFields(parameters._id, parameters.harvesting_function);
    projetToComplete = document.getElementById(parameters._id);
    for (z = 0; z < a[mem][1].length; z = z + 1) {
        projetToComplete[a[mem][1][z]].value = parameters[a[mem][1][z]];
    }
}

function updateListProject() {
    var dateBeforeUpdate  = 0;

    Ink.requireModules(['Ink.Net.Ajax_1'], function (Ajax) {
        var uri = '/harvester/server_time';
        new Ajax(uri, {
            method: 'GET',
            parameters: undefined,
            onSuccess: function (xhrObj, req) {
                var feedback = JSON.parse(req);
                dateBeforeUpdate = feedback.date;
                Ink.requireModules(['Ink.Net.Ajax_1'], function (Ajax) {
                    var uri = '/harvester/projects';
                    new Ajax(uri, {
                        method: 'GET',
                        parameters: undefined,
                        onSuccess: function (xhrObj, req) {

                            var cfeedback = JSON.parse(req);
                            var formToChange, hasBeenProcessed, y, z, i, itExists, idRow,
                                tableElement = document.getElementById("log_table"),
                                tableRows = tableElement.getElementsByTagName("tr"),
                                listIdProcessed = [];
                            for (i = 0; i < tableRows.length; i = i + 1) {
                                idRow = tableRows[i].id.substring(0, tableRows[i].id.indexOf("-row"));
                                itExists = false;
                                cfeedback.forEach(function (project) {
                                    if (project._id === idRow) {
                                        itExists = true;
                                        if (project.date_update > lastRefreshDate) {
                                            formToChange = document.getElementById(idRow);
                                            formToChange.name.value = project.name;
                                            if (formToChange.harvesting_function.value ===  project.harvesting_function) {
                                                for (y = 0; y < a.length; y = y + 1) {
                                                    if (a[y][0] === formToChange.harvesting_function.value) {
                                                        for (z = 0; z < a[y][1].length; z = z + 1) {
                                                            formToChange[a[y][1][z]].value = project[a[y][1][z]];
                                                        }
                                                        break;
                                                    }
                                                }
                                            } else {
                                                formToChange.harvesting_function.value = project.harvesting_function;
                                                updateFields(idRow, project.harvesting_function);
                                                formToChange = document.getElementById(idRow);
                                                for (y = 0; y < a.length; y = y + 1) {
                                                    if (a[y][0] === formToChange.harvesting_function.value) {
                                                        for (z = 0; z < a[y][1].length; z = z + 1) {
                                                            formToChange[a[y][1][z]].value = project[a[y][1][z]];
                                                        }
                                                        break;
                                                    }
                                                }
                                            }
                                        }
                                        listIdProcessed.push(idRow);
                                    }
                                });
                                if (itExists === false) {
                                    document.getElementById(idRow).remove();
                                }
                            }
                            cfeedback.forEach(function (project) {
                                hasBeenProcessed = false;
                                listIdProcessed.forEach(function (Id) {
                                    if (project._id ===  Id) {
                                        hasBeenProcessed = true;
                                    }
                                });

                                if (hasBeenProcessed === false) {
                                    createNewRow(project, tableElement);
                                }
                            });
                            lastRefreshDate = dateBeforeUpdate;
                        }});
                    });
            }});
    });
};



function popup(text, type) {
    var myDiv = document.createElement('div'),
        textInPopup = document.createElement("p");
    myDiv.className = "ink-alert basic " + type;
    textInPopup.textContent = text;
    myDiv.appendChild(textInPopup);
    document.getElementsByTagName('nav')[0].appendChild(myDiv);
    setInterval(function () {myDiv.remove(); }, 4000);
}

function deleteProject(id) {
    var parameters = {};
    parameters.id = id;
    popup("Deleting project ...", "info");
    Ink.requireModules(['Ink.Net.Ajax_1'], function(Ajax) {
        var uri = '/harvester/admin/projectdeletion';
        new Ajax(uri,{
            method: 'GET',
            parameters:  parameters,
            onSuccess: function(xhrObj, req) {
                var feedback = JSON.parse(req);
                popup(feedback.text, feedback.type);
                updateListProject();
            }
        });
    });
}



function sendProject(name) {

    var myForm, mySelect = document.getElementById(name + "-select"),
        parameters = {}, i, myFormInputs;
    if (name === "new") {
        parameters.id = -1;
    } else {
        parameters.id = name;
    }
    if ((mySelect.value !== "") && (mySelect.value)) {
        parameters.harvesting_function = mySelect.value;
        myForm = document.getElementById(name);
        myFormInputs = myForm.getElementsByTagName("input");
        for (i = 0; i < myFormInputs.length; i = i + 1) {
            if (myFormInputs[i].value === "") {
                popup("A field is empty, it is impossible to add a project without all the information...", "error");
                return;
            }
            if ((myFormInputs[i].name !== "send") && (myFormInputs[i].name !== "delete")) {
                parameters[myFormInputs[i].name] = myFormInputs[i].value;
            }
        }
        if (name === "new") {
            popup("Adding a new project to the database...", "info");
        } else {
            popup("Modifying project ...", "info");
        }

        Ink.requireModules(['Ink.Net.Ajax_1'], function(Ajax) {
        var uri = "/harvester/admin/projectoperation";
        new Ajax(uri,{
            method: 'GET',
            parameters:  parameters,
            onSuccess: function(xhrObj, req) {
                var feedback = JSON.parse(req);
                popup(feedback.text, feedback.type);
                updateListProject();
                }
            });
        });
        document.getElementById("new").innerHTML = newRow;
        updateListProject();
    } else {
        popup("A field is empty, it is impossible to add a project without all the information...", "error");
    }
}



function refresh() {
    setTimeout(function () {updateListProject(); refresh(); }, 5000);
}