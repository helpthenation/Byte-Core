
odoo.define('website_image_360.script', function (require) {
"use strict";

    $(document).ready(function () {
        var pic_X=$('.list').offset().left;
        var pic_Y=$('.list').offset().top;
        var pic_W=$('.list').width()/2;
        var pic_H=$('.list').height()/2;
        var center_X=pic_X+pic_W;
        var center_Y=pic_Y+pic_H;
        var movestop=pic_W/10;
        $('.list').mousemove(function(event){
            var mouse_X=event.pageX;
            var mouse_Y=event.pageY;
            if(mouse_X-center_X<=0){
                moveImg(mouse_X,mouse_Y,'left')
            }else{
                moveImg(mouse_X,mouse_Y)
            }
        });
        function moveImg(m_X,m_Y,dir){
            var index=Math.ceil(Math.abs(m_X-center_X)/movestop);
            if(dir){
                $('.list li').eq(index).show().siblings().hide();
            }else{
                $('.list li').eq(18-index).show().siblings().hide();
            }
        }

        $('.360_view').click(function(){
            $('.carousel-inner ,.carousel-control, .product_detail_img').css({'display':'none'});
            $('#image_360').css({'display':'block'});

        });
        $('.carousel-indicators').click(function(){
            $('.carousel-inner,.carousel-control ,.product_detail_img').css({'display':'block'});
            $('#image_360').css({'display':'none'});
        })


    })

})
