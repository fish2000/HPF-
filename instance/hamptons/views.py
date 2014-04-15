
import mimetypes
import simplejson

from os.path import basename
from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.views.decorators.cache import cache_page
from django.db.models import Q
#from django.contrib.auth.decorators import login_required

from hamptons.conf import settings
from hamptons.problem import Problem
from hamptons.models import Hamptonian

class APIError(Problem):
    ''' A problem with an HTTP call to our JSON API
    '''
    pass

class DownloadError(Problem):
    ''' A problem with a file requested for download
    '''
    pass
    
# Cache TTL: (sec) * (min) * number of hours
cache_wrap = settings.DEPLOYED and cache_page(60 * 60 * 12) or never_cache

def apicall(f):
    ''' View decorator for API response view functions:
        
            @apicall
            def yodogg(request, you_like):
                """ Handle a 'Yo Dogg' API request """
                what_i_heard = 'I Heard You Like %s' % you_like
                what_we_put = 'We Put %s In Your %s' % (
                    i_heard_you_like, i_heard_you_like)
                
                # Return a dict, to be JSON-ulated in the response
                return dict(
                    yodogg=what_we_heard,
                    we_put_some=what_we_put)
    
        The @apicall decorator deals with API output boilerplate:
        Preparation of the HTTPResponse object parameters,
        JSON serialization, default values, error handling,
        and other stuff one would rather not waste their time
        repeating ad-nauseum in every Tessar view function.
        
        While functions decorated thusly receive dispatched
        arguments with the same arity as normal Django views --
        but instead of returning an HTTPResponse-like instance,
        they return a dict, which is summarily ensconced in a
        response envelope dict under the 'data' label, which is
        then JSON-ified and returned as the HTTP response body
        to the calling client.
    '''
    @csrf_exempt
    @wraps(f)
    def wrapper(*args, **kwargs):
        status = "ok"
        data = {}
        
        try:
            data = f(*args, **kwargs)
        
        except Problem, err:
            status = err.value
            data = {
                'msg': err.msg,
                'etc': err.etc,
            }
        
        except ObjectDoesNotExist, err:
            status = "fail"
            data = {
                'msg': err.message,
            }
        
        return HttpResponse(
            simplejson.dumps({
                'status': status,
                'data': data,
            }, separators=(',',':')),
            content_type="application/json")
    
    # further decorate function before returning
    return cache_wrap(wrapper)

def download(f):
    ''' View decorator for returning opaque document stream responses
        (e.g. files requested for download by the client):
        
            @download
            def download_pimp_my_ride_episode_avi(request, episode_id=""):
                dogg = PimpMyRideAVI.objects.for_slug(episode_id)
                if not dogg:
                    raise DownloadError('YO DOGG',
                        "Episode Not Found: '%s'" % episode_id)
                
                # Note: key names in dicts returned from @download functions
                # are specific (vs. @apicall funcs, whose returned dicts 
                # may name arbitrary keys as per the implementor's whim)
                return dict(
                    content=dogg.binary_data),
                    file="MTVPresents.PimpMyRide.s01e%s.HDTV.aXXo.avi" % episode_id,
                    type='text/plain', charset=settings.TIKA_CHARSET)
    
        Like @apicall, a function wrapped by @download accepts
        arguments with the same arity as normal Django views;
        instead of returning objects from the HTTPResponse family,
        the function passes back a parameter dict, which is
        massaged into the particular output format, behind
        the scenes.
        
        HOWEVER: unlike @apicall, a @download functions' output dict
        parameters are not arbitrarily crammed into the response,
        irrespective of their names. The @download post-processing logic
        looks specifically for keys in the return value:
        
            - 'content':    This must be a file-like object --
                            something implementing a read() method --
                            rewound and ready to go (or anything else that
                            Django's HTTPResponse API likes). This parameter
                            is the only one that must be specified; it has
                            no default value.
            
            - 'file':       The file name, as suggested to the HTTP client
                            in the 'Content-Disposition' response header.
                            If omitted, a name will be fudged on-the-fly,
                            using the output data's mimetype and the URL path
                            of the client HTTP request.
            
            - 'type':       The client will be told that this is the mimetype
                            of the file it is getting. Defaults to 'text/plain'
                            if omitted (since Tika and Tessar traffic in text,
                            for the most part).
            
            - 'charset':    The client will be told that this is the character
                            set of the data in the file it is getting... literally.
                            If this is specified, the charset string you pass will
                            be tacked on to the mimetype string -- nobody is going
                            to open up the whole UnicodeEncodeError can of worms to
                            try to transcode your data.* The default is UTF-8.
                            FUCK WITH THIS VALUE AT YOUR OWN RISK
                            
        ... Other keys will be silently ignored, and except for 'content', omissions
        will be defaulted accordingly as described above.
        
        * (dogg that is what function defs are about I am merely pointing out that
           this is your game son that's all I mean no disrespect)
    '''
    @csrf_exempt
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        try:
            data = f(request, *args, **kwargs)
        except Problem, err:
            return HttpResponseNotFound(
                "%s: %s %s" % (
                    err.status.upper(), err.msg,
                    err.etc and "(%s)" % err.etc))
        except ObjectDoesNotExist, err:
            return HttpResponseNotFound(
                "NOT FOUND (ObjectDoesNotExist): %s" % err.message)
        
        content_type = data.get('type', 'text/plain')
        file_name = data.get('file',
            "%s%s" % (
                basename(request.path),
                mimetypes.guess_extension(content_type)))
        
        if 'charset' in data:
            content_type = '%s, charset=%s' % (
                content_type,
                data.get('charset',
                    settings.TIKA_CHARSET))
        
        content = data.get('content')
        content_data = hasattr(content, 'read') and content.read() or content
        response = HttpResponse(content_data, content_type=content_type)
        response['Content-Length'] = '%d' % len(content_data)
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        return response
    
    # further decorate function before returning
    return cache_wrap(wrapper)

participant_q = Q(state=0) | Q(state=3)

@apicall
def api_frampton_list(request, lister=""):
    user = Hamptonian.objects.for_username(lister)
    if not user:
        raise APIError('fail', "User not found: %s" % lister)
    return dict(
        owns=user.framptons.exclude(state=3).as_list(),
        participates_in=user.participating_in.exclude(participant_q).as_list())

@apicall
def api_frampton_create(request):
    pass

@apicall
def api_frampton_invite(request, frampton_id="", invitee=""):
    pass

@apicall
def api_frampton_uninvite(request, frampton_id="", uninvitee=""):
    pass

@apicall
def api_frampton_start(request, frampton_id=""):
    pass




def mobile_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(
            reverse('hamptons:mobile',
            kwargs=dict(document_id='index.html')))
    tmpl = get_template('hamptons/_login.html')
    return HttpResponse(tmpl.render(RequestContext(request)))

def frampton(request, frampton='messages'):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('hamptons:mobile_login'))
    tmpl = get_template('hamptons/chat.html')
    return HttpResponse(
        tmpl.render(
            RequestContext(request, dict(
                frampton=frampton,
                settings=settings,
            ))),
        content_type="text/html")

def mobile(request, document_id='index.html'):
    """ Just barf out the F7 template """
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('hamptons:mobile_login'))
    try:
        tmpl = get_template('hamptons/%s' % document_id)
    except TemplateDoesNotExist:
        tmpl = get_template('hamptons/index.html')
    return HttpResponse(
        tmpl.render(
            RequestContext(request, dict(
                settings=settings,
            ))),
        content_type="text/html")

