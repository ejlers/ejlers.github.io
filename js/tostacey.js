
$(document).ready(function(){
    $("button").click(function(){
    	$(".background-img").css({"background-image" : "url('https://media.giphy.com/media/l0HlScP4Pl31ADK8M/giphy.gif')"});
		$("button").hide();
		$(".stacey-text").fadeIn(2000);
		$(".stacey-img").fadeIn(2000);
	});
}); 