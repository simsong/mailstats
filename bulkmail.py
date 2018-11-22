#!/usr/bin/env python36
# encoding: utf-8
#

"""Simson's bulkmail program. None of the others seemed to work.

Here is what goes in config file:

[bulkmail]
msg_file: filename_to_bulkmail

[smtp]
username: username
password: password
server: mail.server.to.use

"""

import re
import sys
import os
import datetime
import mailbox
import email.errors
import email.parser
from email.parser import BytesParser
from email import policy
from subprocess import Popen,PIPE
import smtplib

USE_SENDMAIL=False

def sendmail(config,from_addr,to_addrs,msg):
    """Send out the message by sendmail"""
    if opts.dry_run:
        print("==== Will not send this message: ====\n{}\n====================\n".format(msg))
        return False
    if opts.debug:
        to = re.findall("to:.*$", msg, re.I|re.M)[0:1][0]
        print("Sending mail {}".format(to))
    if USE_SENDMAIL:
        p = Popen(['/usr/sbin/sendmail','-t'],stdin=PIPE)
        p.communicate(msg.encode('utf-8'))
        return True
    host = config['smtp']['server']
    with smtplib.SMTP(host,587) as smtp:
        if args.debug:
            smtp.set_debuglevel(1)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(config['smtp']['username'],config['smtp']['password'])
        smtp.sendmail(from_addr,to_addrs,msg)
                   
def find_fields(msg):
    # Find the fields
    fields = set()
    field_re = re.compile("%([a-zA-Z]+)%")
    for line in msg.split("\n"):
        m = field_re.search(line)
        if m:
            fields.add( m.group(1))
    return fields


def make_msg(config,params):
    """Read message specified in the config file and substitute in the fields. Raise an error if field can't be found. """
    with open(config['bulkmail']['msg_file'],encoding='utf8') as f:
        msg = f.read()

        for field_name in find_fields(msg):
            if field_name in params:
                val = params[field_name]
            elif field_name in config['bulkmail']:
                val = config['bulkmail'][field_name]
            else:
                raise RuntimeError("No {} field in config or params".format(field_name))
            msg = msg.replace(f"%{field_name}%",val)
    return msg

if __name__=="__main__":
    # make sure sys is utf8
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1) 
    import argparse

    a = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                description="Bulk Mail Program")
    a.add_argument("--config",  help="config file with private data", default='config.ini')
    a.add_argument("--test",    help="Sends a test message to the address you specify")
    a.add_argument("--dry-run", help="do not send out email or refile messages", action="store_true")
    a.add_argument("--debug",   help="debug", action="store_true")
    a.add_argument("--addresses", help="input file for addresses")
    a.add_argument("inputs",    nargs="*")
    opts = a.parse_args()

    import configparser
    config = configparser.ConfigParser()
    config.read(opts.config)

    if opts.test:
        to_addr = opts.test
        params = {'to':to_addr,'firstname':"Simson"}
        sendmail(config,'simsong@acm.org',[to_addr],make_msg(config,params))
        exit(1)

    if opts.addresses:
        with open(opts.addresses) as f:
            for line in f:
                name = line.strip()
                msg = make_msg(config,{'to':name})
                sendmail(config,msg)
                
