from __future__ import print_function

import uuid
import json

from tornado.web import Application
import tornado.websocket
import tornado.ioloop
#import tornado.gen

from redis import Redis
from tornadoredis import Client as TornadoRedis
from tornadoredis.pubsub import SockJSSubscriber
from sockjs.tornado import SockJSRouter, conn
from sockjs.tornado.transports import base

# Synchronous Redis client instance (for publishing messages to channels)
redis_sync = Redis()

# Async tornadoredis.Client instance (for channel subscriptions)
redis_async = TornadoRedis()
multiplex = SockJSSubscriber(redis_async)


class IndexPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("template.html", title="PubSub + SockJS Demo")


class SendMessageHandler(tornado.web.RequestHandler):

    def _send_message(self, channel, msg_type, msg, user=None):
        msg = {'type': msg_type,
               'msg': msg,
               'user': user}
        msg = json.dumps(msg)
        redis_sync.publish(channel, msg)

    def post(self):
        message = self.get_argument('message')
        from_user = self.get_argument('from_user')
        to_user = self.get_argument('to_user')
        if to_user:
            self._send_message('private.{}'.format(to_user),
                               'pvt', message, from_user)
            self._send_message('private.{}'.format(from_user),
                               'tvp', message, to_user)
        else:
            self._send_message('system', 'msg', message, from_user)
        self.set_header('Content-Type', 'text/plain')
        self.write('sent: %s' % (message,))


class DummyHandler(base.BaseTransportMixin):
    name = 'sandpiper'
    
    def __init__(self, conn_info):
        self.conn_info = conn_info
    
    def get_conn_info(self):
        return self.conn_info

class MessageHandler(conn.SockJSConnection):
    """ SockJS connection handler. """
    
    OPS = (
        'auth', 'join', 'quit',
        'stat', 'twit', 'post',
        'fdbk', 'omfg', 'noop', 
    )
    
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
    
    def _send_message(self, op, frampton, value):
        self.send(json.dumps({
            'op': op,
            'value': value,
            'val': frampton
        }))
    
    def _federate_frampton_message(self, frampton, message):
        redis_async.publish('frampton.%s' % frampton, json.dumps(dict(
            op='post', user=self.username, value=message)))
    
    def _join_frampton(self, frampton):
        multiplex.subscribe('frampton.%s' % frampton, self)
        self.framptons |= set([frampton])
        self._notify_join_or_quit('join')
        self.send(json.dumps(dict(
            op='fdbk', from_op='join', user=self.username, value=frampton)))
    
    def _quit_frampton(self, frampton):
        multiplex.unsubscribe('frampton.%s' % frampton, self)
        self.framptons.remove(frampton)
        self._notify_join_or_quit('quit')
        self.send(json.dumps(dict(
            op='fdbk', from_op='quit', user=self.username, value=frampton)))
    
    def _get_signing_key(self, username, session_token):
        self.username = username
        self.send(json.dumps(dict(
            op='fdbk', from_op='auth', user=self.user_name, value=self.connection_id)))
    
    def _error(self, error_message):
        self.send(json.dumps(dict(
            op='omfg', user='__piper__', value=error_message)))
    
    def on_open(self, request):
        # Generate a user ID and name to demonstrate 'private' channels
        self.connection_id = str(uuid.uuid4())[:5]
        self.framptons = set()
        
        # Send it to user (TODO: generate signing key)
        self.send(json.dumps(dict(
            op='fdbk', from_op='open', user='__piper__', value=self.connection_id)))
        #self._send_message('uid', self.username, self.connection_id)
        
        # Subscribe to broadcast messages
        multiplex.subscribe('system', self)
    
    def on_message(self, jsonic_message):
        ''' Dispatch the proper operation '''
        # { op: (join | quit | stat | twit | post ...), user: <user-name>, value: <value> }
        message = json.loads(jsonic_message)
        op = message.get('op', 'noop').lower()
        user = message.get('user', None)
        value = message.get('value', None)
        
        if op not in self.OPS:
            self._error("UNKNOWN OP: %s" % op)
            return
        elif op == 'auth':
            # value is Django session token, respond with signing key
            if user is None:
                self._error("OP <AUTH> REQUIRES VALID USER NAME")
                return
            if value is None:
                self._error("OP <AUTH> REQUIRES VALUE = 'SESSION KEY'")
                return
            self._get_signing_key(user, value)
        elif op == 'join':
            if value is None:
                self._error("OP <JOIN> REQUIRES VALUE = 'FRAMPTON TO JOIN'")
                return
            self._join_frampton(value)
        elif op == 'quit':
            if value is None:
                self._error("OP <QUIT> REQUIRES VALUE = 'FRAMPTON TO QUIT'")
                return
            self._quit_frampton(value)
        elif op == 'twit':
            # TODO: cryptographically unsign message
            if user is None:
                self._error("OP <TWIT> REQUIRES VALID USER NAME")
                return
            if value is None:
                self._error("OP <QUIT> REQUIRES VALUE = 'TWITTER MESSAGE TO POST'")
                return
            frampton = message.get('frampton', None)
            if frampton is None:
                self._error("OP <QUIT> REQUIRES PARAM frampton = 'FRAMPTON TO WHICH TO TWEET'")
                return
            # TODO: queue for dispatch to Twitter API
            self._federate_frampton_message(frampton, value)
    
    def on_close(self):
        for frampton in self.framptons:
            self._quit_frampton(frampton)
        multiplex.unsubscribe('system', self)


urls = [
    (r'/', IndexPageHandler),
    (r'/send_message', SendMessageHandler)]
urls += SockJSRouter(MessageHandler, '/sandpiper').urls

application = Application(urls)


if __name__ == '__main__':
    import sys
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