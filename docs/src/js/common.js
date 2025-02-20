/*******************************************************************************************
  GENERAL FUNCTION
*******************************************************************************************/
function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/*******************************************************************************************
  EVENT BINDING
*******************************************************************************************/
$('.navbar-button').click(function(){
    if ($('#navbar').attr("class").includes("navbar-mobile")) {
        $('#navbar').removeClass('navbar-mobile');
        $(this).removeClass('fa-close').addClass('fa-bars');
    } else {
        $('#navbar').addClass('navbar-mobile');
        $(this).removeClass('fa-bars').addClass('fa-close');
    }
})

$('.faq-question').click(function(){
  var index = $(this).attr('class').slice(-2);
  $('.faq-content' + index).toggleClass('collapse');
  if ($(this).find('i').attr('class').includes('down')){
    $(this).find('i').removeClass('fa-chevron-down');
    $(this).find('i').addClass('fa-chevron-up');
  } else {
    $(this).find('i').removeClass('fa-chevron-up');
    $(this).find('i').addClass('fa-chevron-down');
  }
})

/*******************************************************************************************
  WINDOW READY
*******************************************************************************************/
$(window).on('load', function(){
  (adsbygoogle = window.adsbygoogle || []).push({});
})