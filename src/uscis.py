#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang
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
SLEEP_SECONDS = 0.2 # wait SLEEP_SECONDS after each query

def get_parser():
    """set up parser and return it"""
    parser = argparse.ArgumentParser(description='USCIS Tracker')
    parser.add_argument('-s', '--start', type=str, default='YSC2090175300',
            help='Start receipt number')
    parser.add_argument('-n', '--number', type=int, default=2,
            help='Number of cases tracked')
    parser.add_argument('-v', '--verbal', action='store_true',help='Print all status')
    parser.add_argument('-r', '--ratio', action='store_true',help='Print pass ratio.')
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


def get_status(num):
    """get status and info of a single case.
       status: e.g., Card Was Delivered To Me By The Post Office
       info: contains more information
    """
    header = {"User-Agent":"User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
    r= requests.post(USCIS_CASE_TRACK_URL,headers=header,data={"changeLocale":"","appReceiptNum":num,"initCaseSearch":"CHECK STATUS"})
    try:
        s = BeautifulSoup(r.content,"lxml")
        rs = s.find('div',"current-status-sec").text
        rs = re.sub(r'[\t\n\r]',"",rs)
        matches = re.findall(r':.+\+', rs)
        status = ""
        if matches:
            status = matches[0][1:-1].strip()
        info = s.find('div', "rows text-center").text
    except Exception as e:
        status, info = "", ""
    # print(status, info)
    return status, info


def process(receipt_numbers, verbal=False):
    """collect status of all receipt_numbers."""
    statuses = []
    infos = []
    for num in receipt_numbers:
        status, info = get_status(num)
        statuses.append(status)
        infos.append(info)
        if verbal:
            print("{}: {}".format(num, status))
        time.sleep(SLEEP_SECONDS)
    return statuses, infos


def print_statistics(statuses):
    """print statistics of the statuses."""
    npassed = 0
    for status in statuses:
        if not "Case Was Received" in status:
            npassed += 1
    print("total number of cases is {:d}".format(len(statuses)))
    print("total number of passed cases is {:d}".format(npassed))
    assert(len(statuses) > 0)
    print("pass ratio is {:0.2f}%".format(npassed / len(statuses) * 100.0))


def main():
    """main function."""
    parser = get_parser()
    args = parser.parse_args()
    receipt_numbers = generate_receipt_numbers(args.start, args.number)
    statuses, infos = process(receipt_numbers, args.verbal)
    if args.ratio:
        print_statistics(statuses)


if __name__ == "__main__":
    main()
