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
import os
import time
# import subprocess
import sys

# local library
import uscis

EMAIL_FILE = "email.data"
RECEIPTS_FILE = "receipts.data"
SLEEP_SECONDS = 600 # check every 10 min
ON_HOURS = 6


def load_email():
    """load email from email.data."""
    with open(EMAIL_FILE, 'r') as in_f:
        email = in_f.read().strip()
    return email


def load_receipt_nums():
    """load receipt numbers from receipts.data."""
    with open(RECEIPTS_FILE, 'r') as in_f:
        receipt_numbers = [line.strip() for line in in_f if line]
    return receipt_numbers


def watch(email, receipt_numbers):
    """check status change of numbers."""
    records = [[] for i in range(len(receipt_numbers))]
    cur_time = 0
    while cur_time < ON_HOURS * 3600:
        statuses, _ = uscis.process(receipt_numbers, verbal=True)
        for i, status in enumerate(statuses):
            if not records[i] or records[i][-1] != status:
                records[i].append(status)
            if len(records[i]) > 1:
                message = ("Status of {} changes from {} to {}.".
                        format(receipt_numbers[i],records[i][0], records[i][1]))
                command = "echo {} | mail -s \"status change\" {}".format(message, email)
                os.system(command)
        time.sleep(SLEEP_SECONDS)
        cur_time += SLEEP_SECONDS
        print(cur_time)


def main():
    """watch several numbers for status change."""
    email = load_email()
    receipt_numbers = load_receipt_nums()
    watch(email, receipt_numbers)


if __name__ == "__main__":
    main()
