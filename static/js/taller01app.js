
function view_teachers(name, url){
	var json= '{"name":"' + name + '", "url":"' + url +'"}';
	console.log(json)

	$.ajax({
        url: "teachers/list",
        timeout: 1000* 60 * 10, 
        data: {
            department: json
        },
        type: "POST",
        success: function (data) {            
            $('#teachers_div').html(data);
        },
        error: function (xhr, status) {
            alert("Sorry, there was a problem!");
        }
    });
}

function teachers_index(){
    $('#page-wrapper').load('teachers/main', function() {
        if($('#myModal')){
            $('#myModal').modal('show')
        }        
    });
}

function news_index(){
    $('#page-wrapper').load('news/main', function(){
        if($('#allnews_div')){
            show_all_news();
        }
    });
}



function run_filter(method, search_text, not_in){
    var div_id=""
    if(method=="regexp"){
        div_id="#regexp_div";
    }else if(method=="xquery"){
        div_id="#xquery_div";
    }

    $.ajax({
        url: "news/filter",
        data: {
            method: method,
            search_text: search_text,
            not_in: not_in
        },
        type: "POST",
        success: function (data) {            
            $(div_id).html(data);
        },
        error: function (xhr, status) {
            alert("Sorry, there was a problem!");
        }
    });
}

function show_all_news(){
    var div_id="allnews_div"
    $('#allnews_div').load('news/all')
}

function filter_news(){
    var text= $('#search_field').val();
    var not_in = $('#notin_cbox')[0].checked;
    show_all_news();
    run_filter('regexp', text, not_in);
    run_filter('xquery', text, not_in);
}