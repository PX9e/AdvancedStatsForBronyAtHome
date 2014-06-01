var chart;

function graph_line_chart(project_stat, properties, update) {

    var i, y,
        my_dates = ['x'],
        my_properties = {},
        my_columns =[];

    for(y = 0; y < properties.length; y++)
    {
        my_properties[properties[y]] = [properties[y]];
    }

    for(i = 0; i < project_stat.length; i++)
    {
        my_dates.push(new Date(project_stat[i]["date"]*1000));

        for(y = 0; y < properties.length; y++)
        {
            my_properties[properties[y]].push(project_stat[i][properties[y]]);
        }
    }

    for(y = 0; y < properties.length; y++)
    {
        my_columns.push(my_properties[properties[y]]);
    }
    my_columns.push(my_dates);

    if(update == false)
    {
        chart = c3.generate({
        bindto: '#graph_area',
            size: {
            height:  document.getElementById('graph_area').offsetWidth * 0.75,
            width:  document.getElementById('graph_area').offsetWidth - 50
        },
        data: {
          x: 'x',
          columns: my_columns,
          type: 'line'
        },
        axis: {
            x: {
                type: 'timeseries',
                localtime: true,
                tick: {
                    format: '%Y-%m-%d %H:%M:%S',
                    rotate: 90,
                },
                height: 130
            }
        }
        });
    } else { 
        chart.load({
        columns: my_columns
    });
    }

}
