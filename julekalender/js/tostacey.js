
$(document).ready(function(){
  $("button").click(function(){
		$(".start-screen").hide();
		$(".content").fadeIn(2000);
	});
}); 

$(document).ready(function(){
		$(".forward").click(function(){
			$("a").attr("href", "http://www.google.com/")
		});
		$(".back").click(function(){
			$("a").attr("href", "http://www.google.com/")
		});
}); 