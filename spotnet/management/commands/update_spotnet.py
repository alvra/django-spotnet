from django.core.management.base import NoArgsCommand, CommandError
from spotnet.connection import Connection, ConnectError


class Command(NoArgsCommand):
    help = 'Retrieves new posts from the usenet server.'

    can_import_settings = True
    output_transaction = True
    requires_model_validation = True

    def logger_function(self, msg):
        self.stdout.write('%s\n' % msg)

    def handle_noargs(self, **options):
        verbosity = options.get('verbosity', 1)

        conn = Connection(connect=False)
        try:
            conn.connect()
        except ConnectError:
            raise CommandError('Could not connect to the newsserver.')
        else:
            conn.update(self.logger_function)
        finally:
            conn.disconnect()
