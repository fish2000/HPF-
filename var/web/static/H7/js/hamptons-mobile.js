
// Initialize your app
var sockURL = '//asio-otus.local:9001/oceanpkway',
    oceanpkway = new SockJS(sockURL),
    hamptons = new Framework7({
        
        onBeforePageInit: function (page) {},
        onPageInit: function (page) {},
        onPageAfterAnimation: function (page) {},
        onPageBeforeAnimation: function (page) {}
        
    }),
    $$$ = hamptons.$,
    mainView = hamptons.addView('.view-main', {
        // Because we use fixed-through navbar,
        // we can enable dynamic navbar
        dynamicNavbar: true
    });

$$$(document).on('pageInit', function (e) {
    var page = e.detail.page;
    
    console.log("pageInit: ", page.name);
    
    if (page.name === 'messages') {
        //console.log("WE CHATTIN");
        // $$$(".messages .message, .messages .messages-date").hide();
        // var MESSAGES = $$$('#MESSAGES');
        $$$(".messages .message, .messages .messages-date").hide();
        hamptons.initMessages();
    }
});

$$$('#tweet-button').on('click', function (e) {
    var message = $$$('#id_tweeter').val(),
        date = new Date(),
        dateparts = date.toDateString().split(' '),
        timeparts = date.toTimeString().split(' '),
        day = dateparts[0],
        time = timeparts[0].split(':').slice(0, 2).join(':');
    
    console.log("TWEET: ", message);
    oceanpkway.send(message);
    hamptons.addMessage({
        text: message, day: day, time: time, type: 'sent'
    });
});

oceanpkway.onopen = function () {
    console.log("OCEANPKWAY: connected");
};

oceanpkway.onmessage = function (e) {
    var message = e.data,
        date = new Date(),
        dateparts = date.toDateString().split(' '),
        timeparts = date.toTimeString().split(' '),
        day = dateparts[0],
        time = timeparts[0].split(':').slice(0, 2).join(':');
    console.log("OCEANPKWAY: message received");
    console.log("OCEANPKWAY: data = ", e.data);
    hamptons.addMessage({
        text: message, day: day, time: time, type: 'received'
    });
};

oceanpkway.onclose = function () {
    console.log("OCEANPKWAY: disconnected");
};

/*
$$$('#tweeter-button').on('touchend', function (e) {
    console.log("FOCUS UP BOY");
    hamptons.$('#id_tweeter').trigger('click');
});*/

/// get rid of browser address bar
window.addEventListener("load", function () {
	window.setTimeout(function () {
		window.scrollTo(0, 1); // Hide the address bar
	}, 0);
});