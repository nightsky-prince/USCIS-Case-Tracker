#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##################################
#
##################################

# standard library
import argparse
import re
import sys
import time

# 3rd party library
from bs4 import BeautifulSoup
import requests

USCIS_CASE_CHECK_URL = 'https://egov.uscis.gov/casestatus/mycasestatus.do'
SLEEP_SECONDS = 0

def get_parser():
    """set up parser and return it"""
    parser = argparse.ArgumentParser(description='USCIS Checker')
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


class USCIS:

    def __init__(self, parser):
        self.args = parser.parse_args()
        self.nreceived = 0
        self.npassed = 0
        self.receipt_numbers = self._generate_receipt_numbers()
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

    def _generate_receipt_numbers(self):
        """return a list of all receipt numbers."""
        start_receipt_num = self.args.start
        try:
            check_start_receipt_num(start_receipt_num)
        except Exception as e:
            print("Invalid receipt number {:s}.".format(start_receipt_num))
            sys.exit(1)
        loc, base = start_receipt_num[:3], int(start_receipt_num[3:])
        receipt_numbers = []
        for idx in range(self.args.number):
            num = "{}{:d}".format(loc, base + idx)
            if len(num) > 13:
                break
            receipt_numbers.append(num)
        return receipt_numbers

    def _get_status(self, num):
        """get status of a single case."""
        header = {"User-Agent":"User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
        r= requests.post(USCIS_CASE_CHECK_URL,headers=header,data={"changeLocale":"","appReceiptNum":num,"initCaseSearch":"CHECK STATUS"})
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
    uscis_checker = USCIS(parser)
    uscis_checker.process()

if __name__ == "__main__":
    main()
