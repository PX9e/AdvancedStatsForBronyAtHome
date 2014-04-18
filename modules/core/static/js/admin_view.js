/**
 * Created by guillaume on 4/18/14.
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
                x.innerHTML = "<div class='control-group'><label for='module'> " + a[i][1][z] + " :</label><div class='control'><input type='text' name=" +  a[i][1][z] + " value=''></div>";
            }
            break;
        }
    }
    updateListProject();
}

function createNewRow(parameters, table) {
    var newRowCode = "", projetToComplete, mem, harvest_function, z;
    newRowCode = "<form id='" + parameters._id + "' class='ink-form'>";
    newRowCode += "<table class='ink-table bordered vertical-space'>";
    newRowCode += "<tr id='" + parameters._id + "-row'>";
    newRowCode += "<td><input type='text' name='name' value='" + parameters.name + "'></td>";
    newRowCode += "<td><select id='" + parameters._id + "-select' onchange='updateFields(\"" + parameters._id + "\", this.value);' name='harvesting_function' >";

    for (harvest_function in a) {
        if (a[harvest_function][0] === parameters.harvesting_function) {
            newRowCode += "<option selected value='" + a[harvest_function][0] + "'>" + a[harvest_function][0] + "</option>";
            mem = harvest_function;
        } else {
            newRowCode += "<option value=" + a[harvest_function][0] + ">" + a[harvest_function][0] + "</option>";
        }
    }
    newRowCode += "</select></td>";
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
    $.getJSON("/harvester/server_time", undefined, function (feedback) {
        dateBeforeUpdate = feedback.date;
        $.getJSON("/harvester/projects", undefined, function (cfeedback) {
            var formToChange, projetToComplete, mem, myNewCode,
                hasBeenProcessed, headerToDelete, y, z, i, itExists, id,
                tableElement = document.getElementById("log_table"),
                tableRows = tableElement.getElementsByTagName("tr"),
                projectInList, or, listIdProcessed = [], origa, ir;
            for (i = 0; i < tableRows.length; i = i + 1) {
                id = tableRows[i].id.substring(0, tableRows[i].id.indexOf("-row"));
                itExists = false;
                cfeedback.forEach(function (project) {
                    if (project._id === id) {
                        itExists = true;
                        listIdProcessed.push(id);
                        formToChange = document.getElementById(id);
                        if (project.date_update > lastRefreshDate) {
                            formToChange.name.value = project.name;
                            if (formToChange.harvesting_function.value ===  project.harvesting_function) {
                                for (y = 0; i < a.length; i = i + 1) {
                                    if (a[y][0] === formToChange.harvesting_function.value) {
                                        for (z = 0; z < a[y][1].length; z = z + 1) {
                                            formToChange[a[y][1][z]].value = project[a[y][1][z]];
                                        }
                                        break;
                                    }
                                }
                            } else {
                                formToChange.harvesting_function.value = project.harvesting_function;
                                updateFields(id, project.harvesting_function);
                                formToChange = document.getElementById(id);
                                for (y = 0; i < a.length; i = i + 1) {
                                    if (a[y][0] === formToChange.harvesting_function.value) {
                                        for (z = 0; z < a[y][1].length; z = z + 1) {
                                            formToChange[a[y][1][z]].value = project[a[y][1][z]];
                                        }
                                        break;
                                    }
                                }
                            }
                        }
                    }
                });

                if (itExists === false) {
                    headerToDelete = document.getElementById(id);
                    headerToDelete.remove();
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
        });
    });
}

function popup(text, type) {
    var myDiv = document.createElement('div'),
        textInPopup = document.createElement("p");
    myDiv.className = "ink-alert basic " + type;
    textInPopup.textContent = text;
    myDiv.appendChild(textInPopup);
    document.getElementsByTagName('body')[0].appendChild(myDiv);
    setInterval(function () {myDiv.remove(); }, 4000);
}

function deleteProject(id) {
    var parameters = {};
    parameters.id = id;
    $.getJSON("/harvester/admin/projectdeletion", parameters, function (feedback) {popup(feedback); });
    updateListProject();
}



function sendProject(name) {

    var myForm, mySelect = document.getElementById(name + "-select"),
        parameters = {}, i;
    if (name === "new") {
        parameters.id = -1;
    } else {
        parameters.id = name;
    }
    if ((mySelect.value !== "") && (mySelect.value)) {
        parameters.harvesting_function = mySelect.value;
        myForm = document.getElementById(name);
        for (i = 0; i < myForm.elements.length; i = i + 1) {
            if (myForm.elements[i].type === "text") {
                if (myForm.elements[i].value === "") {
                    popup("A field is empty, it is impossible to add a project without all the information...", "error");
                    return;
                }
                parameters[myForm.elements[i].name] = myForm.elements[i].value;
            }
        }
        if (name === "new") {
            popup("Adding a new project to the database...", "");
        } else {
            popup("Modifying project ...", "");
        }
        $.getJSON("/harvester/admin/projectoperation", parameters, function (feedback) {popup(feedback); });
        document.getElementById("new").innerHTML = newRow;
        updateListProject();
    }

}



function refresh() {
    setTimeout(function () {updateListProject(); refresh(); }, 5000);
}