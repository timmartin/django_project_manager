

$(function() {

    $("table tr.week_row td").on("click", function() {
	var selected_task = $('input:radio[name=task]:checked');

	if (selected_task) {
	    $(this).children("span.day_label").text(selected_task.attr("task-name"));
	    var foo = $('input:radio[name=task]:checked').parent();
	    console.log("background is " + foo.css("background-color"));
	    $(this).css("background", foo.css("background-color"));

	    var form_input = $(this).children("input.day_input");
	    form_input.val(selected_task.val());
	}
    });
    
});
