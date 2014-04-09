
import sys

from django.core.management.base import BaseCommand
from optparse import make_option
from clint.textui import colored, puts

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--no-http', '-X', action="store_false",
            dest='http', default=True,
            help="Don't serve status pages via HTTP"),
        make_option('--no-exit', '-N', action='store_false',
            dest='exit', default=True,
            help="Don't call sys.exit() when halting"),
    )
    
    help = ("Runs the HPF Sandpiper (sock.js) server")
    args = '[ip-address | port | ip-address:port]'
    can_import_settings = True
    serve_http = True
    exit_when_halting = True
    
    def exit(self, status=2):
        """ Exit when complete """
        puts("Cleaning up ...")
        puts('')
        if self.exit_when_halting:
            sys.exit(status)
    
    def handle(self, *args, **options):
        self.serve_http = options.get('http')
        self.exit_when_halting = options.get('exit')
        self.quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CTRL-C'
        
        from tornado.ioloop import IOLoop
        from tornado.httpserver import HTTPServer
        from tornado.log import enable_pretty_logging
        from sandpiper.conf import settings
        from sandpiper.server import application
        
        http_server = HTTPServer(application)
        http_server.listen(settings.SANDPIPER_PORT)
        
        puts('Validating models ...')
        self.validate(display_num_errors=True)
        
        puts(colored.cyan("\nDjango version %(version)s, using settings %(settings)r\n"
                          "HPF Sandpiper server running at http://%(addr)s:%(port)s\n"
                          "Quit the server with %(quit_command)s" % dict(
                              version=self.get_version(),
                              settings=settings.SETTINGS_MODULE,
                              addr=settings.SANDPIPER_ADDRESS,
                              port=settings.SANDPIPER_PORT,
                              quit_command=self.quit_command)))
        
        enable_pretty_logging()
        
        try:
            IOLoop.instance().start()
    
        except KeyboardInterrupt:
            puts('')
            puts(colored.yellow("HPF Sandpiper server shutting down"))
        
        finally:
            self.exit(0)
