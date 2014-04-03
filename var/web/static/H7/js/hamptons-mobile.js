// Initialize your app
var hamptons = new Framework7({
        
        onBeforePageInit: function (page) {},
        onPageInit: function (page) {},
        onPageAfterAnimation: function (page) {},
        onPageBeforeAnimation: function (page) {}
        
    }),
    $$$ = hamptons.$,
    mainView = hamptons.addView('.view-main', {
        // Because we use fixed-through navbar we can enable dynamic navbar
        dynamicNavbar: true
    });

$$$(document).on('pageInit', function (e) {
    var page = e.detail.page;
    
    console.log("pageInit: ", page.name);
    
    if (page.name === 'messages') {
        //console.log("WE CHATTIN");
        $$$(".messages .message, .messages .messages-date").hide();
    }
});


/*
$$$('#tweeter-button').on('touchend', function (e) {
    console.log("FOCUS UP BOY");
    hamptons.$('#id_tweeter').trigger('click');
});*/