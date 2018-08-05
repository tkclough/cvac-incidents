"""
Download a file from iamresponding.com. Then, annotate the model with new data.
Finally, email the generated report.
"""
import json
import argparse
from apiclient.discovery import build
from httplib2 import Http
from cvac.fetch_data import download
from cvac.misc_io import get_newest_file, wait_for_file_to_finish
from cvac.annotate import annotate_file
from cvac.email import create_message_with_attachment, send_message, get_creds

def main():
    """
    Entry point for report.py
    """
    # parse arguments
    parser = argparse.ArgumentParser(
        description='Download, annotate, and send report')

    parser.add_argument('--startdate', dest='startdate', type=str,
                        help='Initial date for report (MM/DD/YYYY)')
    parser.add_argument('--enddate', dest='enddate', type=str,
                        help='Final date for report (MM/DD/YYYY)')
    parser.add_argument('--config', type=str, dest='config', default='config.json',
                        help='Where to read config file from')
    parser.add_argument('--dontmail', dest='sendmail', action='store_false',
                        help="Don't send an email")
    parser.add_argument('--source', dest='report_source',
                        help='Instead of downloading, use this file')

    args = parser.parse_args()

    if args.startdate and args.enddate is None:
        parser.error("--startdate requires --enddate")
    elif args.enddate and args.startdate is None:
        parser.error("--enddate requires --startdate")
    elif args.report_source and args.startdate and args.enddate:
        parser.error("--source and --startdate/--enddate are mutually exclusive")
    elif args.report_source is None and (args.startdate is None and args.enddate is None):
        parser.error("must use either --source or --startdate/--enddate")

    if args.report_source:
        args.infile = args.report_source

    with open(args.config) as file:
        config = json.load(file)

    startdate = args.startdate
    enddate = args.enddate

    if args.report_source:
        filename = args.report_source
    else:
        download(config['IAR_username'],
                 config['IAR_password'],
                 startdate,
                 enddate)

        # get new file
        filename = get_newest_file(config['download_dir'])
        print(filename)

        # wait for file to finish
        wait_for_file_to_finish(filename)

    # annotate the file
    annotate_file(filename, config['outfile'], config['model_path'])

    if args.sendmail:
        # get authorization for gmail api
        creds = get_creds(config['tokenfile'], config['credsfile'])

        service = build('gmail', 'v1', http=creds.authorize(Http()))

        message = create_message_with_attachment(
            config['email_from'],
            config['email_to'],
            ('Report {} to {}'.format(startdate, enddate)),
            "Attached is report xls file.",
            config['outfile'])

        send_message(service, 'me', message)


if __name__ == '__main__':
    main()
