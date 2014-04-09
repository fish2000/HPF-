
// Initialize your app
var sockURL = '//asio-otus.local:9001/sandpiper',
    sandpiper = new SockJS(sockURL),
    framp = function (frampton) {
        return function (message) {
            return {
                op: 'twit',
                user: window.SETTINGS['username'],
                frampton: frampton,
                value: message
            };
        };
    },
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
        //hamptons.initMessages();
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
    sandpiper.send(message);
    hamptons.addMessage({
        text: message, day: day, time: time, type: 'sent'
    });
});

sandpiper.onopen = function () {
    console.log("SANDPIPER: connected");
};

sandpiper.onmessage = function (e) {
    var message = e.data,
        date = new Date(),
        dateparts = date.toDateString().split(' '),
        timeparts = date.toTimeString().split(' '),
        day = dateparts[0],
        time = timeparts[0].split(':').slice(0, 2).join(':'),
        payload = JSON.parse(e.data),
        op = payload['op'].lower(),
        user = payload['user'].lower(),
        value = payload['value'].lower(),
        from_op = '';
    
    console.log("SANDPIPER: message received");
    //console.log("SANDPIPER: data = ", e.data);
    
    switch (op) {
        
        /// OP: fdbk / "Feedback" / additional: [from_op]
        case 'fdbk':
            console.log("OP: <<fdbk>>");
            console.log("USER: ", user);
            console.log("VALUE: ", value);
            
            from_op = payload['from_op'].lower();
            
            if (from_op === 'open') {
                sandpiper.send(JSON.stringify({
                    op: 'auth',
                    user: window.SETTINGS['username'],
                    value: 'YO DOGG',
                }));
            } else if (from_op === 'auth') {
                
            }
            
            break;
        
        default:
            console.log("UNKNOWN OP: ", op.upper());
            console.log("USER: ", user);
            console.log("VALUE: ", value);
            break;
    }
    
    hamptons.addMessage({
        text: message, day: day, time: time, type: 'received'
    });
};

sandpiper.onclose = function () {
    console.log("SANDPIPER: disconnected");
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