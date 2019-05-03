# This module batches data into optimal size batches for Kinesis.
# Kinesis has the following input constraints:
#    - the maximum size of one record is 1 MB
#    - the maximum size of all records in one batch is 5 MB
#    - maximum number of records in a batch is 500
#
#
# The batch_data takes in an array of records and 
# returns an iterator over optimal batches.
# Records are kept in the same order that they are
# in the original array.

import sys

ALLOWED_FORMATTING_VALUES = ["string", "json"]


class KinesisBatcher:

	def __init__(self, input_format="string", record_max_size=1000000, batch_max_size=5000000, max_records_per_batch=500):
		self.unmodified_data = []
		self.record_max_size = record_max_size
		self.batch_max_size = batch_max_size
		self.max_records_per_batch = max_records_per_batch
		self.discarded = 0

		if input_format not in ALLOWED_FORMATTING_VALUES:
			raise ValueError("{} is not allowed as a format, allowed values are {}".format(input_format, ALLOWED_FORMATTING_VALUES))

		self.input_format = input_format

	def is_too_large(self, record):

		return self.get_record_size(record) > self.record_max_size

	def get_data(self, data):
		'''
		Iterate over the given array. If array item is too
		large (would go over Kinesis' record size limit), discard it.
		:param data

		'''

		for d in data:

			if self.is_too_large(d):
				# Simply discard items that are too large
				self.discarded += 1
				continue

			yield d

		return

	def get_record_size(self, record):
		'''
		Return size of the given record. If records are in json format, 
		check that PartitionKey(Unicode string) and Data(bytes) together do not
		exceed the maximum payload size. If records are strings, we just
		check the size of the string.
		'''
		

		if self.input_format == "json":
			try:
				return len(record["Data"]) + len(record["PartitionKey"].encode("utf-8"))
			except KeyError:
				raise ValueError("Record {} was invalid json for Kinesis".format(record))
			except AttributeError:
				raise ValueError("Record {} invalid; Expected partition key to be string, data bytes".format(record))

		elif self.input_format == "string":
			return len(record.encode("utf-8"))

	def batch_data(self, data):
		'''
		Batches the given data according to KinesisBatcher's constraints. Returns an iterator over the batches,
		that is, each iteration returns a batch (an array).
		'''
		batch = []

		data_for_batch = self.get_data(data)
		current_batch_size = 0
		current_records_in_batch = 0

		while True:

			try:

				next_item = next(data_for_batch)

				if current_batch_size + self.get_record_size(next_item) > self.batch_max_size or current_records_in_batch == self.max_records_per_batch:
					# This batch cannot fit any more items, so return it
					yield batch

					# Reset counters
					batch = []
					current_batch_size = 0
					current_records_in_batch = 0

				batch.append(next_item)
				current_batch_size += self.get_record_size(next_item)
				current_records_in_batch += 1

			except StopIteration:

				print("All data batched")
				print("Discarded {} records that went over the max record size limit of {}".format(self.discarded, self.batch_max_size))
				yield batch
				return


# if __name__ == "__main__":

# 	batcher = KinesisBatcher(["i", 2, "ii", "iii", "i", "i", "iw", "iasda", "a"])
# 	iterator = batcher.batch_data()
# 	print(next(iterator))
# 	print(next(iterator))

# 	## Instead of initialising with data
# 	# should we batcher = KinesisBatcher(maxdata=1)
# 	# batcher.batch(["a", "b", "c"])
# 	# for data in batcher.batch(["a", "b", "c"])

