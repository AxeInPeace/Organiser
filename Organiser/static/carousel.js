$(".carousel").click(function(){
    var cur_date = new Date($(".schedule_table_date").val());
    var amount = 0
    if ($(this).hasClass("carousel-left"))
        amount = -7;
    else if ($(this).hasClass("carousel-right"))
        amount = 7;
    cur_date.setDate(cur_date.getDate() + amount);


    $.ajax({
		url: "{% url 'change_schedule_table' %}",
		async: false,
		data: {
			year: cur_date.getFullYear(),
			month: cur_date.getMonth(),
			day: cur_date.getDate(),
		},
		});
	$(".schedule_table_date").val(cur_date);
});

