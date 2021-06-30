$(function(){
    $('body').on('click', '.list-group-item', function(){
      $('.list-group-item').removeClass('active');
      $(this).closest('.list-group-item').addClass('active');
    });
  });
$('.option-select ul li:nth-child(1) a').click(function (e) { 
    
    e.preventDefault();
    console.log($('.phan1').offset().top);
    $('html,body').animate({scrollTop:$('.phan1').offset().top-120},800);
});
$('.option-select ul li:nth-child(2) a').click(function (e) { 
    
    e.preventDefault();
    console.log($('.phan1').offset().top);
    $('html,body').animate({scrollTop:$('.phan2').offset().top-45},800);
});
$('.option-select ul li:nth-child(3) a').click(function (e) { 
    
    e.preventDefault();
    console.log($('.phan1').offset().top);
    $('html,body').animate({scrollTop:$('.phan3').offset().top-45},800);
});