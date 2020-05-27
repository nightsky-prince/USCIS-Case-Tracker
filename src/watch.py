#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang
##################################
# watch cases and email when status
# changes
# put receipt numbers (each case per line) in receipts.data
# put email address in email.data
##################################

# standard library
from datetime import datetime
import os
import time
# import subprocess
import sys

# local library
import uscis

EMAIL_FILE = "email.data"
RECEIPTS_FILE = "receipts.data"
SLEEP_SECONDS = 600 # check every 10 min
MAX_HOURS = 12 #


def print_current_datetime():
    """print current datetime to CLI."""
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string)	


def load_email(filename):
    """load email from file."""
    try:
        with open(filename, 'r') as in_f:
            email = in_f.read().strip()
            assert(email.count('@') == 1)
    except:
        print(f'{filename} does not exist.')
        sys.exit(1)
    return email


def load_receipt_nums(filename):
    """load receipt numbers from file (one receipt per line)."""
    try:
        with open(filename, 'r') as in_f:
            receipt_numbers = [line.strip() for line in in_f if line]
    except:
        print(f'{filename} does not exist.')
        sys.exit(1)
    return receipt_numbers


def watch(email, receipt_numbers):
    """check status change of numbers."""
    records = [[] for i in range(len(receipt_numbers))]
    cur_time = 0
    while cur_time < MAX_HOURS * 3600:
        print_current_datetime()
        statuses, _ = uscis.process(receipt_numbers, verbal=True)
        for i, status in enumerate(statuses):
            if not records[i] or records[i][-1] != status:
                records[i].append(status)
            if len(records[i]) > 1:
                message = ("Status of {} changes from {} to {}.".
                        format(receipt_numbers[i],records[i][0], records[i][1]))
                records[i] = [records[i][-1]]
                # email the message
                command = "echo {} | mail -s \"status change\" {}".format(message, email)
                os.system(command)
        time.sleep(SLEEP_SECONDS)
        cur_time += SLEEP_SECONDS


def main():
    """watch several numbers for status change."""
    email = load_email(EMAIL_FILE)
    receipt_numbers = load_receipt_nums(RECEIPTS_FILE)
    watch(email, receipt_numbers)


if __name__ == "__main__":
    main()
