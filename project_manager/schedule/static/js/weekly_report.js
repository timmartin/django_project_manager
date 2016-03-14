

$(function() {

    $("table tr.week_row td").on("click", function() {
	var selected_task = $('input:radio[name=task]:checked');

	if (selected_task) {
	    $(this).children("span.day_label").text(selected_task.attr("task-name"));

	    $(this).css("background",
			selected_task.parent().css("background-color"));

	    var form_input = $(this).children("input.day_input");
	    form_input.val(selected_task.val());
	}
    });
    
});
