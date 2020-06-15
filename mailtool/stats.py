import os
import re
import csv
import logging
import mailbox
import sys

from collections import defaultdict
from email.header import Header

assert sys.version>'3.0.0'

from albert.AbstractAlbertProcessor import AbstractAlbertProcessor
from albert.Albert import Albert


class SimpleMailStats(AbstractAlbertProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.senders  = defaultdict(int)
        self.subjects = defaultdict(int)
        self.receivers = defaultdict(int)

    def printTopN(self, title, statobj, N):
        print(f"{title}:")
        counts = [(b[1],b[0]) for b in statobj.items()]
        for (ct,(value,key)) in enumerate(sorted(counts,reverse=True)):
            print(value,key)
            if ct>=N:
                break
        print("")
            
    def process_message(self,msg):
        if 'To' in msg:
            self.receivers[ msg['To']] += 1

        if 'Cc' in msg:
            self.receivers[ msg['Cc']] += 1

        if 'From' in msg:
            try:
                self.senders[ msg['From']] += 1 
            except:
                self.senders[msg['From'].__str__()]+=1           
   
        if 'subject' in msg:
            try:    
                self.subjects[ msg['subject']] += 1
            except:
                self.subjects[msg['subject'].__str__()]+=1

    def report(self):
        self.printTopN('Receivers',self.receivers,10)
        self.printTopN('Senders',self.senders,10)
        self.printTopN('Subjects',self.subjects,10)
        
    def print_message(self,message):
        if message['date'] == None:
            date = "No date"
        else:
            date = message['date']

        if message['from'] == None:
            From = "No From"
        else:
            From = message['from']

        if message['subject'] == None:
            subject = "No Subject"
        else:
            subject = message['subject']    

        print(date)
        print(From)
        print(subject)
        print("\n")


if __name__=="__main__":
    import argparse, resource
    parser = argparse.ArgumentParser(description='Demo program that uses albert to scan a mailbox and print stats',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("path", nargs="*", help="Files or Directories to scan")
    args = parser.parse_args()
    sms  = SimpleMailStats()

    # Get a scanner

    alb = Albert(sms)  # get a scanner with the specified callback
    for p in args.path:
        alb.scan(p)             # scan

    sms.report()
