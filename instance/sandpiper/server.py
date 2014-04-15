from __future__ import print_function

import sys
import uuid
import json

from tornado.web import Application, RequestHandler
from tornadoredis import Client as TornadoRedis
from tornadoredis.pubsub import SockJSSubscriber
from sockjs.tornado import SockJSRouter, conn
from django.core.signing import Signer, BadSignature, SignatureExpired

from sandpiper.redpool import redpool as redis_sync
from sandpiper.structs import RedisDict

# Async tornadoredis client (for channel pub/sub ONLY)
# use redpool for all other redis q's
redis_async = TornadoRedis()
multiplex = SockJSSubscriber(redis_async)

class IndexPageHandler(RequestHandler):
    def get(self):
        self.render("template.html",
            title="PubSub + SockJS Demo")

class MessageHandler(conn.SockJSConnection):
    """ SockJS connection handler. """
    
    OPS = (
        'auth', 'join', 'quit',
        'stat', 'twit', 'post',
        'fdbk', 'omfg', 'noop', 
    )
    
    def json(self, **kwblob):
        return self.send(json.dumps(kwblob))
    
    def _notify_join_or_quit(self, op='join'):
        system_endpoints = list(multiplex.subscribers['system'].keys())
        message = json.dumps({
            'op': op,
            'user': self.username,
            'value': [{ 
                'id': endpt.connection_id,
                'name': endpt.username } for endpt in system_endpoints] })
        
        if system_endpoints:
            system_endpoints[0].broadcast(system_endpoints, message)
    
    def _federate_frampton_message(self, frampton, message):
        redis_sync.publish('frampton.%s' % frampton, json.dumps(dict(
            op='post', user=self.username, frampton=frampton, value=message)))
    
    def _join_frampton(self, frampton):
        multiplex.subscribe('frampton.%s' % frampton, self)
        self.framptons |= set([frampton])
        self._notify_join_or_quit('join')
        self.json(op='fdbk', from_op='join',
            user=self.username, value=frampton)
    
    def _quit_frampton(self, frampton):
        multiplex.unsubscribe('frampton.%s' % frampton, self)
        self.framptons.remove(frampton)
        self._notify_join_or_quit('quit')
        self.json(op='fdbk', from_op='quit',
            user=self.username, value=frampton)
    
    def _check_signing_key(self, username, signing_key):
        self.username = username
        self.stash = RedisDict(username, redis_sync)
        if 'signing_key' not in self.stash:
            self.json(op='omfg', from_op='auth',
                user=self.username, value="NO STASHED SIGNING KEY")
        if self.stash['signing_key'] != signing_key:
            self.json(op='omfg', from_op='auth',
                user=self.username, value="WTF KIND OF FAKENESS IS THIS [piper: %s, frampton: %s]" % (
                    self.stash['signing_key'], signing_key))
        self.signing_key = signing_key
        self.signer = Signer(key=signing_key)
        self.json(op='fdbk', from_op='auth',
            user=self.username, value=self.connection_id)
    
    def _unsign(self, signed_string):
        out = False
        if not hasattr(self, 'signer'):
            return False
        try:
            out = self.signer.unsign(signed_string)
        except BadSignature:
            return False
        except SignatureExpired:
            return False
        return out
    
    def _error(self, error_message):
        print("ERROR > %s" % error_message, file=sys.stdout)
        return self.json(op='omfg',
            user='__piper__', value=error_message)
    
    def on_open(self, request):
        # Generate a user ID and name to demonstrate 'private' channels
        self.connection_id = str(uuid.uuid4())[:5]
        self.framptons = set()
        
        # Send it to the user
        self.json(op='fdbk', from_op='open',
            user='__piper__', value=self.connection_id)
        
        # Subscribe to broadcast messages
        multiplex.subscribe('system', self)
    
    def on_message(self, jsonic_message):
        ''' Dispatch the proper operation '''
        # { op: (join | quit | auth | twit ...), user: <username>, value: <value> }
        try:
            message = json.loads(jsonic_message)
        except ValueError:
            return self._error("BAD JSON MESSAGE: %s" % jsonic_message)
        
        op = message.get('op', 'noop').lower()
        user = message.get('user', None)
        value = message.get('value', None)
        
        if op not in self.OPS:
            return self._error("UNKNOWN OP: %s" % op)
        
        elif op == 'auth':
            # value is signing key, respond with current connection ID
            if user is None:
                return self._error("OP <AUTH> REQUIRES VALID USER NAME")
            if value is None:
                return self._error("OP <AUTH> REQUIRES VALUE = 'SIGNING KEY'")
            self._check_signing_key(user, value)
        
        elif op == 'join':
            if value is None:
                return self._error("OP <JOIN> REQUIRES VALUE = 'FRAMPTON TO JOIN'")
            unsigned_value = self._unsign(value)
            if not unsigned_value:
                return self._error("OP <JOIN> VALUE w/ BAD SIGNATURE = '%s'" % value)
            self._join_frampton(unsigned_value)
        
        elif op == 'quit':
            if value is None:
                return self._error("OP <QUIT> REQUIRES VALUE = 'FRAMPTON TO QUIT'")
            unsigned_value = self._unsign(value)
            if not unsigned_value:
                return self._error("OP <QUIT> VALUE w/ BAD SIGNATURE = '%s'" % value)
            self._quit_frampton(unsigned_value)
        
        elif op == 'twit':
            if user is None:
                return self._error("OP <TWIT> REQUIRES VALID USER NAME")
            if value is None:
                return self._error("OP <TWIT> REQUIRES VALUE = 'TWITTER MESSAGE TO POST'")
            frampton = message.get('frampton', None)
            if frampton is None:
                return self._error("OP <TWIT> REQUIRES PARAM frampton = 'FRAMPTON TO WHICH TO TWEET'")
            unsigned_value = self._unsign(value)
            if not unsigned_value:
                return self._error("OP <TWIT> VALUE w/ BAD SIGNATURE = '%s'" % value)
            # TODO: queue for dispatch to Twitter API
            self._federate_frampton_message(frampton, unsigned_value)
    
    def on_close(self):
        for frampton in self.framptons:
            self._quit_frampton(frampton)
        multiplex.unsubscribe('system', self)


urls = [
    (r'/', IndexPageHandler)]
urls += SockJSRouter(MessageHandler, '/sandpiper').urls

application = Application(urls)


if __name__ == '__main__':
    from clint.textui import puts, colored
    from sandpiper.conf import settings
    
    from tornado.ioloop import IOLoop
    from tornado.httpserver import HTTPServer

    http_server = HTTPServer(application)
    http_server.listen(settings.SANDPIPER_PORT)

    puts(colored.cyan("HPF Sandpiper server running at %s:%s\n"
                      "Quit the server with CTRL-C" % (
                          settings.SANDPIPER_ADDRESS, settings.SANDPIPER_PORT)))

    try:
        IOLoop.instance().start()

    except KeyboardInterrupt:
        puts(colored.red("HPF Sandpiper shutting down"))
    
    finally:
        sys.exit(0)