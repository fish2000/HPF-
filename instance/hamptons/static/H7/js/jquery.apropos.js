
(function ($, _, T) {
    
    $.extend({
        
        new: function (elem) {
            /// create a new jQuery-wrapped DOM element,
            /// unbound to the current page
            return $(document.createElement(elem));
        },
        
        querystring: function () {
            /// turn a keyed data object into a query string
            /// alphabetically sorted by key and appended to a URL
            /// e.g. { yo: 'dogg', iheard: 'you like queries' }
            /// becomes http://yodogg.com/x?iheard=you%20like%20queries&yo=dogg
            var querydict = arguments[0] || {},
                url = arguments[1] || "",
                omit = arguments[2] || [];
            return _.chain(querydict)
                .omit(omit)
                .pairs()
                .sortBy(function (pair) { return pair[0]; })
                .filter(function (pair) { return (pair[0] !== null
                    && typeof pair[0] !== "undefined"); })
                .reduce(
                    function (memo, kv) {
                        var value = (
                            kv[1] === null || typeof kv[1] === "undefined")
                                ? ''
                                : kv[1];
                        return "{0}&{1}={2}".format(memo,
                            kv[0].toString().uriencode(),
                            value.toString().uriencode());
                    },
                    url.suffixWith("?"))
                .value();
        },
        
        dictpath: function () {
            /// turn a object's values into sequential URL path segments,
            /// alphabetically sorted by key and appended to a URL
            /// e.g. { yo: 'dogg', iheard: 'you like path segments' }
            /// becomes http://yodogg.com/x/you-like-path-segments/dogg
            var querydict = arguments[0] || {},
                url = arguments[1] || "",
                omit = arguments[2] || [];
            return _.chain(querydict)
                .omit(omit)
                .pairs()
                .sortBy(function (pair) { return pair[0]; })
                .filter(function (pair) { return (pair[1] !== null
                    && typeof pair[1] !== "undefined"); })
                .reduce(function (memo, pair) {
                    return "{0}/{1}".format(
                        memo, pair[1].toString().slugify()); },
                url.suffixWith('/'))
                .value();
        },
        
        hash: function (hashable) {
            /// hash anything you pass in (defaults to MD5)
            if (typeof hashable === "undefined") {              return "undefined".MD5(); }
            if (typeof hashable === "string") {                 return hashable.MD5(); }
            if (typeof hashable.elementname !== "undefined") {  return hashable.elementname().MD5(); }
            
            var jsonable = _.isObject(hashable) || _.isArray(hashable),
                functype = _.isFunction(hashable);
            if (jsonable && !functype) {
                try {
                    return (JSON.stringify(hashable)).MD5();
                } catch (e) {
                    return hashable.toString().MD5();
                }
            }
            
            if (typeof hashable.html !== "undefined") {         return hashable.html().MD5(); }
            return hashable.toString().MD5();
        },
        
        default_results_examiner: function (results) {
            var status = typeof results !== 'undefined';
            status = status && (results !== null);
            status = status && results.hasOwnProperty('status');
            status = status && results['status'].toString().toLowerCase() == 'ok';
            return status;
        }
        
    });
    
    $.fn.extend({
        
        hash: function () {
            var $this = $(this),
                hash_memo = $this.data('apropos-hash'),
                hash_out = undefined;
            if (typeof hash_memo !== "undefined") {
                return hash_memo;
            }
            hash_out = $.hash($this);
            $this.data('apropos-hash', hash_out);
            return hash_out;
        },
        
        new: function (elem_type) {
            return $.new(elem_type).appendTo(this);
        },
        
        apropos: function (url_) {
            /// bind the JSON data retrieved from the specified URL
            /// to an 'QED' event on $(this), e.g.
            /// $('.myshit').apropos('http://yodogg.com/x');
            var $that = $(this),
                results_examiner_func = arguments[1] || $.default_results_examiner,
                url_maker_func = arguments[2] || $.dictpath;
            
            this.each(function () {
                var $this = $(this);
                $this.on('apropos', function(e, options) {
                    var url = url_maker_func(
                            $that.queryopts(options), url_),
                        url_key = $.hash(url),
                        data = $that.data(url_key),
                        results_are_valid = false,
                        force = (
                            typeof options.force !== "undefined" && options.force);
                    
                    if (force || typeof data === "undefined") {
                        /// GET NEW DATA, BECAUSE NONE ALREADY EXISTS
                        $.when($.getJSON(url))
                            .done(function (apropos_results) {
                                try {
                                    results_are_valid = results_examiner_func.call(
                                        $this, apropos_results);
                                } catch (exc) {
                                    results_are_valid = false;
                                }
                                if (results_are_valid) {
                                    //console.log(">> APROPOS: XHR results OK");
                                    $that.data(url_key, apropos_results['data']);
                                    $this.triggerHandler('inquiry',
                                        [url_key, true, options]);
                                } else {
                                    //console.log(">> APROPOS: XHR results are NOT OK");
                                    //console.log(">> APROPOS: results = ", apropos_results);
                                    $this.triggerHandler('failure',
                                        [url_key, options]);
                                }})
                            .fail(function (xhr, status_, apropos_results) {
                                //console.log(">> APROPOS: XHR request FAILED");
                                //console.log(">> APROPOS: status = ", status_);
                                //console.log(">> APROPOS: message = ", apropos_results);
                                $this.triggerHandler('failure',
                                    [url_key, options]);
                            }
                        );
                    } else {
                        /// USE THE ALREADY EXISTING DATA
                        //console.log(">> APROPOS: triggering inquiry for data: ", data);
                        $this.triggerHandler('inquiry',
                            [url_key, false, options]);
                    }
                });
            });
            
            return $that;
        },
        
        WRT: function (url) {
            /// bind the JSON data retrieved from the specified URL
            /// to an 'QED' event on $(this), e.g.
            /// $('.myshit').apropos('http://yodogg.com/x');
            var $that = $(this),
                results_examiner_func = arguments[1] || $.default_results_examiner;
            
            this.each(function () {
                var $this = $(this);
                $this.on('apropos', function(e, options) {
                    /// W/R/T posts: data is always anew
                    $.when($.post(url, $this.queryopts(options), 'json'))
                        .done(function (apropos_results) {
                            var results_are_valid = false;
                            try {
                                results_are_valid = results_examiner_func.call(
                                    $this, apropos_results);
                            } catch (exc) {
                                results_are_valid = false;
                            }
                            if (results_are_valid) {
                                //console.log(">> W/R/T: XHR results OK");
                                var url_key = $.hash(url);
                                $that.data(url_key, apropos_results['data']);
                                $this.triggerHandler('inquiry',
                                    [url_key, true, options]);
                            } else {
                                //console.log(">> W/R/T: XHR results are NOT OK");
                                //console.log(">> W/R/T: results = ", apropos_results);
                                $this.triggerHandler('failure',
                                    [null, options]);
                            }})
                        .fail(function (xhr, status_, apropos_results) {
                            //console.log(">> W/R/T: XHR request FAILED");
                            //console.log(">> W/R/T: results = ", apropos_results);
                            $this.triggerHandler('failure',
                                [null, options]);
                        }
                    );
                });
            });
            
            return $that;
        },
        
        inthecaseof: function (datum) {
            /// bind the passed piece of arbitrary data
            /// to an 'QED' event on $(this), e.g.
            /// $('.myshit').inthecaseof({ yo: 'dogg' });
            var $that = $(this);
            
            this.each(function () {
                var $this = $(this);
                
                $this.on('apropos', function (e, options) {
                    var datum_key = $.hash(options);
                    $that.data(datum_key, datum);
                    $this.triggerHandler('inquiry',
                        [datum_key, false, options]);
                });
            });
            
            return $that;
        },
        
        failure: function (failure_func) {
            /// called when an apropos() or WRT() fetch
            /// returns an error, e.g.:
            /// $('.myshit')
            ///     .apropos('http://yodogg.com/x')
            ///     .inquire(function (data) {
            ///         //console.log('Yo Dogg: ',data);
            ///     })
            ///     .failure(function (url_key, opts) {
            ///         alert("NO DOGG");
            ///     }
            /// );
            var $that = $(this);
            
            this.each(function () {
                var $this = $(this);
                
                $this.on('failure', function (e, url_key, options) {
                    failure_func(url_key, options);
                });
            });
            
            return $that;
        },
        
        inanycase: function (final_func) {
            /// called when an apropos() or WRT() fetch
            /// returns anything at all, e.g.:
            /// $('.myshit')
            ///     .apropos('http://yodogg.com/x')
            ///     .inquire(function (data) {
            ///         //console.log('Yo Dogg: ',data);
            ///     })
            ///     .inanycase(function (url_key, opts) {
            ///         alert("Shit May Or May Not Be Fucked");
            ///     }
            /// );
            var $that = $(this);
            
            this.each(function () {
                var $this = $(this),
                    isitoveryet = function (e, url_key, options) {
                        return final_func(url_key, options);
                    };
                
                $this.on({
                    failure: isitoveryet,
                    findings: isitoveryet
                });
            });
            
            return $that;
        },
        
        defaults: function () {
            var $that = $(this),
                defaults_ = arguments[0] || null,
                default_value = arguments[1] || null,
                existent = $that.data('defaults');
            
            existent = typeof existent === "object" ? existent : {};
            
            if (defaults_) {
                if (typeof defaults_ === "object") {
                    /// it's an object hashtable, merge it in
                    $that.data('defaults', _(existent).extend(defaults_));
                } else if (typeof defaults_ === "string") {
                    /// it's a string key
                    if (default_value) {
                        existent[defaults_] = default_value;
                        $that.data('defaults', existent);
                    } else {
                        if (defaults_ in existent) {
                            return existent[defaults_];
                        }
                        return undefined;
                    }
                }
            } else {
                /// nothing was passed in, return the defaults hashtable
                return existent;
            }
            
            return $that;
        },
        
        omit: function () {
            var $that = $(this),
                omits = arguments[0] || null,
                existent = $that.data('omit');
            
            existent = typeof existent === "object" ? existent : [];
            
            if (omits) {
                if (typeof omits === "object") {
                    /// it's a list, merge it in
                    $that.data('omit', existent.concat(_.toArray(omits)));
                } else if (typeof omits === "string") {
                    /// it's a single string key, add it
                    $that.data('omit', _(existent)
                        .chain()
                        .push(omits)
                        .uniq()
                        .value());
                }
            } else {
                /// nothing was passed in, return the omits list
                return _.toArray(existent);
            }
            
            return $that;
        },
        
        queryopts: function () {
            var $that = $(this),
                defaults = _.clone($that.defaults()),
                omit = [].concat($that.omit()),
                options = arguments[0] || {},
                union = _.defaults(options, defaults),
                intersection = _(union).omit(omit);
            return intersection;
        },
        
        elementname: function () {
            var $this = $(this),
                id = $this.attr('id'),
                classes = $this.attr('class'),
                idname = (typeof id !== 'undefined'
                    ? id.toString().prefixwith('#')
                    : undefined),
                classnames = (typeof classes !== 'undefined' ? classes
                    .split(' ')
                    .map(function (cls) { return cls.prefixwith('.'); })
                    .join('') : undefined);
            
            return (typeof idname !== 'undefined')
                ? idname
                : ((typeof classnames !== 'undefined')
                    ? classnames
                    : "<unknown>");
        },
        
        slug: function () {
            return $(this).elementname().slugify();
        },
        
        inquire: function (inquiry_func) {
            /// bind a function to receive the data output from either
            /// an apropos() URL or an inthecaseof() datum
            /// to an 'QED' event on $(this), e.g.
            /// $('.myshit')
            ///     .apropos('http://yodogg.com/x')
            ///     .inquire(function (data) {
            ///         //console.log('Yo Dogg: ',data);
            ///     }
            /// );
            /// ... an optional second function can be passed to
            /// pre-process the options sent by the 'QED' event:
            /// $('.myshit')
            ///     .apropos('http://yodogg.com/x')
            ///     .inquire(function (data) {
            ///         //console.log('Yo Dogg: ',data);
            ///     }, function (options) {
            ///         return $.extend(options, {
            ///             recursive: true,
            ///             action: 'PUT'
            ///         });
            ///     }
            /// );
            var pre_inquiry_opts = arguments[1] || {},
                event_namespace = arguments[2] || 'default',
                event_name = "inquiry.{0}".format(
                    event_namespace),
                $that = $(this),
                pre_inquiry_func;
            
            if (!_.isFunction(pre_inquiry_opts)) {
                pre_inquiry_func = function (opts, $root) {
                    return _(pre_inquiry_opts).extend(opts);
                };
            } else {
                pre_inquiry_func = pre_inquiry_opts;
            }

            this.each(function() {
                var $this = $(this);
                                
                $this.on('QED', function (e, options) {
                    options = pre_inquiry_func.apply($this,
                        [_.extend(
                            _.clone($that.defaults()),
                            options),
                        $that]) || options;
                    $this.on(event_name, function (e, _key, fresh_fetch, options) {
                        var findings = inquiry_func.apply($this, [
                                $that.data(_key),
                                _key, fresh_fetch, options]);
                        $this.off(event_name);
                        $this.triggerHandler('findings', [options, findings]);
                    });
                    
                    console.log(
                        ">> QED ({0}): ".format(
                            $this.elementname()),
                        options);
                    
                    $this.triggerHandler('apropos', [options]);
                });
            });
            return $that;
        },
        
        incorporate: function (template) {
            /// A convenience function call to set up an inquire() callback
            /// to replace the contents of the element upon which it is called
            /// with the contents of a template (named in the eponymous variable)
            /// processed with the data returned from the apropos() query.
            /// TO WIT:
            /// 
            /// <script type="text/x-handlebars-template"
            ///     id="in-your-template" class="template">
            ///     <p>I heard you like {{ in_your }}</p>
            /// </script>
            /// ... and then ...
            /// $('.myshit')
            ///     .apropos('http://yodogg.com/x')
            ///     .incorporate('in-your-template')
            ///     .QED();
            ///
            /// incorporate() can optionally accept a pre-inquiry callback function
            /// as a second argument (see notes on inquire() for details):
            ///
            /// $('.myshit')
            ///     .apropos('http://yodogg.com/x')
            ///     .incorporate('in-your-template', function (opts, $root) {
            ///         return $.extend(opts, {
            ///             you_like: "template function shortcuts"
            ///         });
            ///     }).QED();
            var $that = $(this),
                template_func = $.template(template),
                pre_inquiry = arguments[1] || function (opts, $root) {};
            return this.each(function () {
                var $this = $(this);
                $this.inquire(function (data) {
                    $this.html(template_func(data));
                    return data;
                }, pre_inquiry);
            });
        },
        
        QED: function() {
            /// trigger a bound inquiry function to execute on
            /// any of the sources (apropos() URLs or inthecaseof()
            /// data elements) attached to the jQuery collection,
            /// taking into consideration any options passed, e.g.
            /// $('.myshit')
            ///     .apropos('http://yodogg.com/x')
            ///     .inquire(function (data) {
            ///         console.log('Yo Dogg: ',data);
            ///     }).QED({
            ///         'iheard': what_do_you_like(data['heard'])
            ///     });
            var options = arguments[0] || {},
                findings_callback = arguments[1] || null,
                $that = $(this);
            
            this.each(function () {
                var $this = $(this);
                
                /// unbind any previous 'findings' handlers
                $this.off('findings');
                
                /// if a callback was passed, bind it
                if (findings_callback !== null) {
                    $this.on('findings', function (e, options_, findings) {
                        findings_callback.apply($this, [options_, findings]);
                        $this.off('findings');
                    });
                }
                
                $this.triggerHandler('QED', options);
            });
            
            return $that;
        }
        
    });
    
    ///// ALIASES /////
    $.fn.options = $.fn.defaults;
    
    ///// PRE-CACHE ALL TEMPLATES /////
    $(document).ready(function () {
        var $body = $('body');
    
        $('script.template').each(function () {
            /// compile all <script>s with the 'template' class
            /// (using Handlebars now but that may change)
            var $template = $(this),
                template_key = "template:{0}".format(
                    $template.slug()),
                template_func = T.compile(
                    $template.html());
            $body.data(template_key, template_func);
        });
    
        $.extend({
        
            template: function (elem) {
                /// return a template function (if any)
                /// from the page-wide data cache
                if (typeof elem === "string") { elem = elem.prefixwith("#"); }
                var $elem = $(elem),
                    template_func = $body.data(
                    "template:{0}".format(
                        $elem.slug())),
                    existant = (typeof template_func !== "undefined");
                /// log a message for unknown template names
                if (!existant) {
                    console.log(
                        ">> UNKNOWN TEMPLATE NAME passed to $.template: ",
                        $elem.elementname());
                }
                /// unknown templates return a function that logs a message
                /// about the lack of template when called
                return (existant) ? template_func : function (data) {
                    console.log(
                        ">> UNDEFINED TEMPLATE FUNCTION called with data: ",
                        data, ", name: ", $elem.elementname());
                };
            }
        
        });
    });
    

})(jQuery, _, Handlebars);
