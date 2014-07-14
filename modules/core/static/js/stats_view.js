var current_data_project;
var data_array;
var properties_to_print = [];

function getProjectData(project_name) {
    Ink.requireModules(['Ink.Net.Ajax_1'], function(Ajax) {
        var uri = '/stats/' + project_name;
        var tempdata = {};
        new Ajax(uri, {
            method: 'GET',
            onSuccess: function(xhrObj, req) {
                current_data_project = JSON.parse(req);
                data_array = new Array();
                var my_menu = document.getElementById("second_menu");
                var propertiesList = Object.getOwnPropertyNames(current_data_project[0].team_data);
                for(var i = 0 ; i < current_data_project.length;i++) {
                    tempdata = current_data_project[i].team_data;
                    tempdata["date"] =  current_data_project[i]["date"];
                    data_array.push(tempdata);
                }
                my_menu.innerHTML = "";
                for(var y = 0 ; y < propertiesList.length; y++) {
                    if(current_data_project[0].team_data[propertiesList[y]] != null) {
                        my_menu.appendChild(create_list_element(propertiesList[y]));
                    }
                }
                document.getElementById("graph_area").innerHTML = "";
                properties_to_print = [];
                properties_to_print.push("total_credit");
                graph_line_chart(data_array, properties_to_print, false);
            }
        });
    });
}

function create_list_element(value) {
    var my_li = document.createElement('li');
    var my_a = document.createElement('a');
    my_a.href ="#";

    if(value=="total_credit") {
        my_li.className = "heading active";
    }
    my_a.innerText=value;
    my_a.onclick = function () {
        if(properties_to_print.indexOf(this.innerText) != -1) {
            if(properties_to_print.length != 1) {
                chart.unload(this.innerText);
                properties_to_print.splice(properties_to_print.indexOf(this.innerText), 1);
                my_li.className = "";
            } else {
                my_li.className = "heading active";
            }
        } else {
             my_li.className = "heading active";
             properties_to_print.push(this.innerText);
             graph_line_chart(data_array, properties_to_print, true);
        }
    };
    my_a.text=value;
    my_li.appendChild(my_a);
    return my_li;
}

//function create_title_and_description() {
//    var title = document.createElement('h3');
//    var description = document.createElement('p');
//
//    title.innerText=;
//    description.innexText=;
//
//}


function create_date_form() {

    var form_div = document.createElement('div');
    var form = document.createElement('form');


    var input_date_start = document.createElement('input');

    var input_date_end = document.createElement('input');

    form.appendChild(input_date_start);
    form.appendChild(input_date_end);
    form_div.appendChild(form);

}