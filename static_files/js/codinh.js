document.addEventListener('DOMContentLoaded',function(){
    var codinh=document.querySelector('.codinh');
    console.log(codinh.offsetTop);
    var vtcodinh=codinh.offsetTop;
    console.log(codinh.offsetTop+600);
    var vtdunglai=codinh.offsetTop+1500;

    window.addEventListener('scroll',function(){
        if (window.pageYOffset>vtcodinh) {
            codinh.classList.add('dunglai');
        } else {
            codinh.classList.remove('dunglai')
        }
    })
    window.addEventListener('scroll',function(){
        if (window.pageYOffset>vtdunglai) {
            codinh.classList.remove('dunglai');
        } 
    })
},false)
$(window).scroll(function () { 
    console.log($('.codinh').offset().top);
});
