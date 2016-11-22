
$(document).ready(function(){
    $("button").click(function(){
    	$(".background-img").css({"background-image" : "url('https://media.giphy.com/media/hbgGNb6Pa64bS/giphy.gif')", "opacity": "0.8"});
		$("button").hide();
		$(".stacey-text").fadeIn(2000);
	});
});