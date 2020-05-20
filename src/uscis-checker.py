#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##################################
# track uscis case status
##################################

# standard library
import argparse
import re
import sys
import time

# 3rd party library
from bs4 import BeautifulSoup
import requests

USCIS_CASE_TRACK_URL = 'https://egov.uscis.gov/casestatus/mycasestatus.do'
SLEEP_SECONDS = 0.2

def get_parser():
    """set up parser and return it"""
    parser = argparse.ArgumentParser(description='USCIS Tracker')
    parser.add_argument('-s', '--start', type=str, default='YSC2090175300',
            help='Start receipt number')
    parser.add_argument('-n', '--number', type=int, default=2,
            help='Number of cases tracked')
    parser.add_argument('-v', '--verbal', action='store_true',help='Print all status')
    return parser


def check_start_receipt_num(s):
    """check start receipt number."""
    # TODO: check location code is valid
    assert(len(s) == 13)
    assert(s[:3].isalpha())
    assert(s[3:].isdigit())


def generate_receipt_numbers(start_receipt_num, cnt):
    """return a list of all receipt numbers."""
    try:
        check_start_receipt_num(start_receipt_num)
    except Exception as e:
        print("Invalid receipt number {:s}.".format(start_receipt_num))
        sys.exit(1)
    loc, base = start_receipt_num[:3], int(start_receipt_num[3:])
    receipt_numbers = []
    for idx in range(cnt):
        num = "{}{:d}".format(loc, base + idx)
        if len(num) > 13:
            break
        receipt_numbers.append(num)
    return receipt_numbers


class USCIS:

    def __init__(self, args, receipt_numbers):
        self.args = args
        self.receipt_numbers = receipt_numbers
        print(self.receipt_numbers)
        self.nreceived = 0
        self.npassed = 0
        self.status = []

    def process(self):
        """process all the receipts in sequence."""
        for num in self.receipt_numbers:
            self._get_status(num)
            time.sleep(SLEEP_SECONDS)
        print("total number of cases is {:d}".format(self.npassed + self.nreceived))
        print("total number of passed cases is {:d}".format(self.npassed))
        print("pass ratio is {:0.2f}%".format(self.npassed / (self.npassed + self.nreceived) * 100.0))
        """
        if self.args.verbal:
            for num, status in zip(self.receipt_numbers, self.status):
                print("{}: {}".format(num, status))
        """


    def _get_status(self, num):
        """get status of a single case."""
        header = {"User-Agent":"User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
        r= requests.post(USCIS_CASE_TRACK_URL,headers=header,data={"changeLocale":"","appReceiptNum":num,"initCaseSearch":"CHECK STATUS"})
        try:
            s=BeautifulSoup(r.content,"lxml")
            rs = s.find('div',"current-status-sec").text
            rs = re.sub(r'[\t\n\r]',"",rs)
            matches = re.findall(r':.+\+', rs)
            status = ""
            if matches:
                status = matches[0][1:-1].strip()
            rs_info = s.find('div', "rows text-center").text
            self.status.append(status)
            if "Case Was Received" in rs: # and ("I-765" in rs_info or "I-129" in rs_info):
                self.nreceived += 1
            elif "Produced" in rs or "Delivered" in rs or "Mailed To Me" in rs or "Picked" in rs:
                self.npassed += 1
            if self.args.verbal:
                print("{}: {}".format(num, status))
        except Exception as e:
            pass

def main():
    """main function."""
    parser = get_parser()
    args = parser.parse_args()
    receipt_numbers = generate_receipt_numbers(args.start, args.number)
    uscis_checker = USCIS(args, receipt_numbers)
    uscis_checker.process()

if __name__ == "__main__":
    main()
