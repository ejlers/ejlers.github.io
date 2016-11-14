 $(document).ready(function (){
     
    $( ".explore" ).click(function() {
        var id = $(this).data('id');

        var className = '.case-' + id,
            _className = 'case-' + id,
            showClassName = '.case-' +id+ '-show';

        var cases = $(".case");        
        var numberOfCases = cases.length / 2;


        $( className ).slideToggle( "slow" );

        $.map(cases, function (x) {
            var $x = $(x);
            
            if(! $x.hasClass(_className)) {
                $x.hide();
            }
            
        });

        for(var i = 1; i <= numberOfCases; i++) {
            var caseToShowClass = 'case-' + (i) + '-show';
            if (i != id) {
                $('.'+caseToShowClass).show();
            }
        }

        $('html, body').animate({
            scrollTop: $(className).offset().top
        }, 500);

    });

    $("#click-3").click(function (){
        $('html, body').animate({
            scrollTop: $("#headline-3").offset().top
        }, 500);
    });
});

$(document).ready(function (){
    $("#back-to-top").click(function (){
        $("html, body").animate({ scrollTop: 0 
        }, 500);
    });
});