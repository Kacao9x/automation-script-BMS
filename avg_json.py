#!/usr/bin/python

'''
usage: avg_json.py [-h] [-n N]

find the average of the numbers

optional arguments:
  -h, --help        show this help message and exit
  -n N, --number N  append a number to the list before calculating average
'''

import argparse as a, json as j

FILE = "numbers.json"

try:
	f = open(FILE, 'r')
	jsonData = j.load(f)
	numbers = jsonData["numbers"]
	f.close()
except IOError:
	numbers = []

p = a.ArgumentParser(description="find the average of the numbers")
p.add_argument("-n", "--number", type=int, metavar='N',
               help="append a number to the list before calculating average")

args = p.parse_args()
if args.number != None:
	numbers.append(args.number)

with open(FILE, 'w') as f:
	jsonData["numbers"] = numbers
	f.write(j.dumps(jsonData))

f.close()

total = float(sum(numbers))
size = len(numbers)
print "Average:", total / (size if size else 1)

