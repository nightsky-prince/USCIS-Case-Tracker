# USCIS Case Tracker
Track USCIS case status

**Usage:**

1. check a range of receipt numbers

`python uscis.py -s YSC2090175300 -n 10 -v -r`

The above code checks status of receipt numbers from
YSC2090175300 to YSC2090175309.

-v is used to print status of each receipt number to CLI.

-r is used to print pass ratio to CLI.

1. watch one or more receipt numbers and email a message when status changes

`python watch.py`

You need to put receipt numbers to src/receipts.data (one number per line) and an email address to src/email.data.
