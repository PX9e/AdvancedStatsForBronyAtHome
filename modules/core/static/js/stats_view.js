var current_data_project;


function getProjectData(project_name) {
    Ink.requireModules(['Ink.Net.Ajax_1'], function(Ajax) {
        var uri = '/stats/' + project_name;
        new Ajax(uri,{
            method: 'GET',
            onSuccess: function(xhrObj, req) {
                current_data_project = JSON.parse(req);
                var data_array = new Array();
                for(var i = 0 ; i < current_data_project.length;i++)
                {
                    data_array.push(current_data_project[i]);
                }
                document.getElementById("graph_area").innerHTML = "";
                console.log(data_array);
                graphA(data_array);
            }
        });
    });

}