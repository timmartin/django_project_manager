

$(function() {

    $("table tr.week_row td").on("click", function() {
	var val = $('input:radio[name=task]:checked').attr("task-name");
	$(this).text(val);
    });
    
});
