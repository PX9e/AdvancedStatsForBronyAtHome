var current_data_project;
var data_array;

function getProjectData(project_name) {
    Ink.requireModules(['Ink.Net.Ajax_1'], function(Ajax) {
        var uri = '/stats/' + project_name;
        var tempdata = {};
        new Ajax(uri,{
            method: 'GET',
            onSuccess: function(xhrObj, req) {
                current_data_project = JSON.parse(req);
                data_array = new Array();
                var my_menu = document.getElementById("second_menu");
                console.log(current_data_project[0]);
                var propertiesList = Object.getOwnPropertyNames(current_data_project[0].data);
                for(var i = 0 ; i < current_data_project.length;i++)
                {
                    console.log(current_data_project[i].data);
                    tempdata = current_data_project[i].data;
                    tempdata["date"] =  current_data_project[i]["date"];
                    data_array.push(tempdata);
                }
                my_menu.innerHTML = "";
                for(var y = 0 ; y < propertiesList.length; y++)
                {
                    console.log(propertiesList[y]);
                    my_menu.appendChild(create_list_element(propertiesList[y]))
                }
                console.log(current_data_project[0].data.size);

                document.getElementById("graph_area").innerHTML = "";

                graphA(data_array, "total_credit");
            }
        });
    });
}

function create_list_element(value){

    var my_li = document.createElement('li');
    var my_a = document.createElement('a');
    my_a.href ="#";
    my_a.onclick = function () {graphA(data_array, value);};
    my_a.innerText=value;
    my_a.text=value;
    my_li.appendChild(my_a);
    return my_li;
}