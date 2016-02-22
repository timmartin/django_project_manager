google.charts.load('current', {'packages':['gantt']});
google.charts.setOnLoadCallback(drawChart);

function daysToMilliseconds(days) {
    return days * 24 * 60 * 60 * 1000;
}

function updateChart(chart, data) {
    var options = {
        height: 275
    };

    var chartData = new google.visualization.DataTable();
    chartData.addColumn('string', 'Task ID');
    chartData.addColumn('string', 'Task Name');
    chartData.addColumn('string', 'Resource');
    chartData.addColumn('date', 'Start Date');
    chartData.addColumn('date', 'End Date');
    chartData.addColumn('number', 'Duration');
    chartData.addColumn('number', 'Percent Complete');
    chartData.addColumn('string', 'Dependencies');
    
    for (row in data) {
	var end_date = new Date(data[row].end_date);
	end_date.setHours(23);
	chartData.addRow([data[row].name,
			  data[row].name,
			  data[row].resource,
			  new Date(data[row].start_date),
			  end_date,
			  null,
			  0,
			  data[row].depends_on]);
    }
    
    chart.draw(chartData, options);
}

function drawChart() {    
    var chart = new google.visualization.Gantt(document.getElementById('chart_div'));

    $.ajax({url: "/schedule/gantt-json",
            success: function(data) {updateChart(chart, data);}});
}
