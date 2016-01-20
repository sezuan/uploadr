#!/usr/bin/env python


import os
import sys
import logging
import requests
import argparse

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout, XMPPError

from pprint import pprint

class Uploadr(ClientXMPP):

    filename = None

    def __init__(self, jid, password, filename, shorten_url):
        ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.session_start)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin("xep_0363") # HTTP File Upload
        self.filename = filename
        self.shorten_url = shorten_url


    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        # Upload File

        try:
            get_url = self['xep_0363'].upload_file(self.filename)
            if self.shorten_url:
                print self.short(get_url)
            else:
                print get_url
        except IqError as err:
            logging.error('There was an error getting the roster')
            logging.error(err.iq['error']['condition'])
            self.disconnect()
            return
        except IqTimeout:
            logging.error('Server is taking too long to respond')
            self.disconnect()
            return
        except XMPPError:
            logging.error('Server doesn\'t support http_upload. Or something else went wrong.')
            self.disconnect()
            return
        except:
            logging.error('Something went very wrong.')
            self.disconnect()
            return

        self.disconnect(wait=True)

    def short(self, url):
        r = requests.post("https://yerl.org/", data = '"' + url + '"')
        if r.status_code == 200:
            return r.text.strip('"')
        else:
            return "url shortener failed."

if __name__ == '__main__':

    logging.basicConfig(level=logging.WARN,
                        format='%(levelname)-8s %(message)s')

    # Read Config
    jid = None
    password = None
    try:
        f = open(os.path.expanduser("~") + "/" + ".uploadrc", "rb")
        jid = f.readline().strip()
        password = f.readline().strip()
    except:
        pass

    # Parse Opts
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jid", help="JID", required=not(jid))
    parser.add_argument("-p", "--password", help="Password", required=not(password))
    parser.add_argument("-s", "--short", help="Use https://yerl.org to shorten URL", action="store_true", required=False, )
    parser.add_argument("filename", help="File to upload")
    args = parser.parse_args()

    if args.jid:
        jid = args.jid
    if args.password:
        password = args.password

    xmpp = Uploadr(jid, password, args.filename, args.short)
    try:
        xmpp.connect()
        xmpp.process(block=True)
    except KeyboardInterrupt:
        pass
