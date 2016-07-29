from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings

from django_regnskap.django_dropbox.decorator import get_client,db_client_update_file
from django_regnskap.regnskap.lib.export import ExelYearView

from dropbox.rest import ErrorResponse

from datetime import date
import os

class Command(BaseCommand):
    help = 'Backup regnskap data to dropbox accounts'

    def add_arguments(self, parser):
        parser.add_argument("username", nargs='+')

    def handle(self, *args, **options):
        # Update database_dump.sql
        self.dump_db()
        # Update excel workbooks for this year and last year
        if settings.REGNSKAP_FIRST_YEAR == date.today().year:
            excel_years = [date.today().year]
        else:
            excel_years = [date.today().year-1,date.today().year]
        for year in excel_years:
            e = ExelYearView(year)
            e.save(self.excel_filename(year))


        # iterate over all users
        user_objects = get_user_model().objects
        users = [user_objects.get_by_natural_key(opt) for opt in options['username']]
        for user in users:
            client = get_client(user)
            for year in range(settings.REGNSKAP_FIRST_YEAR,date.today().year+1):
                # Copy bilag files to Dropbox
                db_folder = "/regnskap/%d"%year
                server_folder = os.path.join(settings.MEDIA_ROOT,str(year))
                try:
                    files = client.metadata(db_folder)['contents']
                except ErrorResponse as e:
                    if e.status == 404:
                        client.file_create_folder(db_folder)
                        files = client.metadata(db_folder)['contents']
                    else:
                        raise e
                files = [f["path"].lower() for f in files]
                for f in os.listdir(server_folder):
                    path = db_folder+"/"+f
                    if path.lower() not in files:
                        with open(os.path.join(server_folder,f)) as handle:
                            client.put_file(db_folder + "/" + f, handle)
            # Copy db backup
            with open("/home/ivarne/media/db-backup.sql") as handle:
                db_client_update_file(client,"/regnskap/db-backup.sql",handle)
            # copy last 2 excel workbooks
            for year in excel_years:
                with open(self.excel_filename(year)) as handle:
                    db_client_update_file(client, "/regnskap/regnskap%s.xslx"%year,handle)
    def dump_db(self):
        sqluser = settings.DATABASES.get('default').get('USER')
        db_host = settings.DATABASES.get('default').get('HOST')
        db_name = settings.DATABASES.get('default').get('NAME')
        #password= settings.DATABASES.get('default').get('PASSWORD')
        #pythonanyware somehow sets the database passwoerd
        os.system("mysqldump --skip-dump-date -u '%s' -h '%s' '%s' > /home/ivarne/media/db-backup.sql" %(sqluser, db_host, db_name))
    
    def excel_filename(self, year):
        return os.path.join(settings.MEDIA_ROOT,"regnskap%s.xlsx"%year)
