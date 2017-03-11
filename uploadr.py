#!/usr/bin/env python


import os
import sys
import logging
import requests
import argparse

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout, XMPPError

from pprint import pprint


class InvalidRecipient(Exception):
    pass


class Uploadr(ClientXMPP):

    filename = None

    def __init__(self, jid, password, filename, shorten_url, notify):
        ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.session_start)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin("xep_0363") # HTTP File Upload
        self.filename = filename
        self.shorten_url = shorten_url
        self.notify = notify

    def good_recipient(self, jid):
        if jid == self.boundjid.bare:
            return True
# FIXME: Eigentlich sollte der Roster schon da sein.
        roster = self.get_roster(block=True, timeout = 10)
        jids = roster['roster']['items']
        if jid in jids:
            if jids[jid]['subscription'] == 'both':
                return True
            else:
                return False
        else:
            return False

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        # Upload File

        try:
            if self.notify:
                if self.good_recipient(self.notify):
                    get_url = self['xep_0363'].upload_file(self.filename)
                    self.send_message(mto=self.notify, mbody=get_url, mtype="chat")
                else:
                    raise InvalidRecipient
            else:
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
        except InvalidRecipient:
            logging.error('Invalid recipient. The recipient must be in the roster and subscribed.')
            self.disconnect()
            return
        except:
            raise
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
    parser.add_argument("-n", "--notify", help="Send a notification.", default = False, required=False, )
    parser.add_argument("filename", help="File to upload")
    args = parser.parse_args()

    if args.jid:
        jid = args.jid
    if args.password:
        password = args.password

    xmpp = Uploadr(jid, password, args.filename, args.short, args.notify)
    xmpp.connect()
    xmpp.process(block=True)
