$(document).ready(function(){
    $('#hamburger').click(function(e) {
        e.stopPropagation();
        $('#main_nav ul').slideToggle();
    });
});