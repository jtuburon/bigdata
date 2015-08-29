
function view_teachers(name, url){
	var json= '{"name":"' + name + '", "url":"' + url +'"}';
	console.log(json)

	$.ajax({
        url: "teachers/",
        data: {
            department: json
        },
        type: "POST",
        success: function (data) {
            console.log(data)
            $('#teachers_div').html(data);
        },
        error: function (xhr, status) {
            alert("Sorry, there was a problem!");
        }
    });
}