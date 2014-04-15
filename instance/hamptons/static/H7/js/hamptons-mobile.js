
(function (SETTINGS, URLS, Framework7, SockJS, $) {

    // Initialize your app
    var signing_key = SETTINGS['signing_key'],
        username = SETTINGS['username'],
        hostname = SETTINGS['hostname'] || 'localhost',
        sockURL = '//{0}:9001/sandpiper'.format(hostname),
        sandpiper = new SockJS(sockURL),
    
        framptize = function (frampton_name) {
            return function (message) {
                return {
                    op: 'twit',
                    user: username,
                    frampton: frampton_name,
                    value: message.sign(signing_key)
                };
            };
        },
        framp = framptize('__wat__'),
    
        join = function (frampton_name) {
            sandpiper.json({
                op: 'join',
                user: username,
                value: frampton_name.sign(signing_key)
            });
        },
        quit = function (frampton_name) {
            sandpiper.json({
                op: 'quit',
                user: username,
                value: frampton_name.sign(signing_key)
            });
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
        $$$(".message, .messages-date").hide();
    
        if (page.name.startswith('frampton-')) {
            window.frampton = page.name.replace(/^frampton-/, '');
            console.log("WE CHATTIN: ", window.frampton);
            join(window.frampton);
        }
    });

    $$$('#tweet-button').on('click', function (e) {
        var message = $$$('#id_tweeter').val();
    
        console.log("TWEET: ", message);
        sandpiper.json(framp(message));
    });

    sandpiper.json = function () {
        return sandpiper.send(JSON.stringify(
            arguments[0] || { op: 'noop' }
        ));
    }

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
            op = payload['op'],
            user = payload['user'],
            value = payload['value'],
            from_op = payload['from_op'];
    
        console.log("SANDPIPER: message received");
        //console.log("SANDPIPER: data = ", e.data);
    
        console.log("OP: <<{0}>>".format(op));
        console.log("USER: ", user);
        console.log("VALUE: ", value);
        console.log("FROM OP: ", from_op);
    
        switch (op) {
        
            case 'join':
                /// Join notice. OP: join, VAL: (user for user in frampton)
                /// Broadcast when a user joins a Frampton channel
                /// (currently, produced for all users and channels)
                break;
        
            case 'quit':
                /// Quit notice. OP: quit, VAL: (user for user in frampton)
                /// Broadcast when a user leaves (quits) a Frampton channel
                /// (currently, produced for all users and channels)
                break;
        
            case 'omfg':
                /// Error message. OP: omfg, VAL: "Error Message Text"
                /// Sent in response to an error condition (usually in leu
                /// of a 'fdbk' message)
                hamptons.alert(
                    "SANDPIPER FREAKOUT:\n" + value);
                break;
        
            case 'post':
                /// Posted message. OP: post, VAL: "Post Message Text"
                if (payload['frampton'] == window.frampton) {
                    hamptons.addMessage({
                        text: value, day: day, time: time,
                        type: user == username ? 'sent' : 'received'
                    });
                }
                break;
        
            case 'fdbk':
                /// Feedback. OP: fdbk, ARGS: [from_op]
                /// Sandpiper's "ack" response to Frampton ops
            
                if (from_op === 'open') {
                    sandpiper.json({
                        op: 'auth',
                        user: username,
                        value: signing_key,
                    });
                } else if (from_op === 'auth') {
                    //join(window.frampton);
                } else if (from_op === 'join') {
                    window.frampton = value;
                    framp = framptize(window.frampton);
                } else if (from_op === 'quit') {
                    window.frampton = undefined;
                    framp = framptize('__wat__');
                } else if (from_op === 'twit') {
                    /// NOOP!
                }
            
                break;
        
            default:
                console.log("UNKNOWN OP: ", op.upper());
                console.log("USER: ", user);
                console.log("VALUE: ", value);
                break;
        }
    
    };

    sandpiper.onclose = function () {
        console.log("SANDPIPER: disconnected");
    };
    
    /// get rid of browser address bar
    window.addEventListener("load", function () {
    	window.setTimeout(function () {
    		window.scrollTo(0, 1); // Hide the address bar
    	}, 0);
    });
    
    
    
    $(document).ready(function () {
        var $listbox = $('#framptons-list-box');
        
        console.log('>>>> YO DOGG <<<<');
        $listbox
            .apropos(URLS['api_frampton_list'])
            .incorporate('#framptons-list');
            
        hamptons.showPreloader("Loading Framptons...");
        $listbox.QED({}, function (opts, findings) {
            hamptons.hidePreloader();
        });
    });

})(window.SETTINGS, window.URLS, Framework7, SockJS, jQuery);
