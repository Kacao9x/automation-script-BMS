from lib.echoes_database import *
import unittest
import bson
import numpy as np
import datetime


class mapp(object):
	_class 		= None
	_debug 		= None
	_debug_level = None

	def __init__(self, debug = False):
		self._debug = debug
		self._class = self.__class__.__name__
		return

	def close(self):
		return

	# Prints messages with function and class
	def dprint(self, txt, timestamp=False, error=False, level=1):

		if level <= self._debug_level:
			if self._debug or error:
				function_name = sys._getframe(1).f_code.co_name
				if timestamp:
					print("  " + str(
						datetime.datetime.now()) + " " + self._class + ":" + function_name + "(): " + txt)
				else:
					print(
							"  " + self._class + ":" + function_name + "(): " + txt)



class Test(unittest.TestCase):
	# echoes_db = database(database='cycler-data')

	def test_one(self):
		echoes_db = database(database='cycler-data')
		lookup_stage = {
			'$lookup': {
				'from'		: "cycler-test",									# name of foreign collection
				'localField': "timestamp",
				'foreignField': "timestamp",
				'as'		: 'battery_details'											# new field in a document
			},
		}

		projection = {
			'$project': {
				'_id': 0,
				'SoH': 1,
				'SoC': 1,
				'Date/Time': 1,
				'en(Wh)':1,
				'current':1,
				'cap(Ah)':1,
				'volt': 1
			}}
		sort_stage = {'$sort': {'_id': 1}}

		pipeline = [
			lookup_stage,
			sort_stage,
			projection,
		]

		echoes_db.aggregation(pipeline, collection='TC06')


		echoes_db.close()
		return True

	def test_two(self):

		return True


	# echoes_db.close()


if __name__ == 'main':
    unittest.main()