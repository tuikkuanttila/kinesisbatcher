'''
KinesisBatcher batches data into optimal size batches for Kinesis.
Kinesis has the following input constraints:
   - the maximum size of one record is 1 MB
   - the maximum size of all records in one batch is 5 MB
   - maximum number of records in a batch is 500


The batch_data takes in an array of records and 
returns an iterator over optimal batches.
Records are kept in the same order that they are
in the original array.
'''




class KinesisBatcher:
	'''
	Create a new instance of KinesisBatcher.

	:param string input_format: The format the array records have, can be string or json for dicts of type {'Data' : b'data', 'PartitionKey' : 'k'}
	:param int record_max_size: Maximum size for records to be accepted into the batch, in bytes. Default 1048576, Kinesis' limit. Cannot be greater than 1048576.
	:param int batch_max_size: Maximum size of batch in total, in bytes. Default 5242880, Kinesis' limit. Cannot be greater than 5242880.
	:param int max_records_per_batch: Maximum number of records per batch. Default 500, Kinesis' limit. Cannot be greater than 500.
	'''

	def __init__(self, input_format="string", record_max_size=1048576, batch_max_size=5242880, max_records_per_batch=500):
		'''
		Create a new instance of KinesisBatcher.

		:param string input_format: The format the array records have, can be string or json for dicts of type {'Data' : b'data', 'PartitionKey' : 'k'}
		:param int record_max_size: Maximum size for records to be accepted into the batch, in bytes. Default 1048576, Kinesis' limit. Cannot be greater than 1048576.
		:param int batch_max_size: Maximum size of batch in total, in bytes. Default 5242880, Kinesis' limit. Cannot be greater than 5242880.
		:param int max_records_per_batch Maximum number of records per batch. Default 500, Kinesis' limit. Cannot be greater than 500.
		:returns: A KinesisBatcher
		:rtype: kinesisbatcher.KinesisBatcher 
		:raises ValueError: if initialisation values are invalid
		'''

		if record_max_size > 1048576 or record_max_size < 0:
			raise ValueError("Invalid record_max_size. Maximum record size is 1048576 bytes.")

		if batch_max_size > 5242880 or batch_max_size < 0:
			raise ValueError("Invalid batch_max_size. Maximum batch size is 5242880 bytes.")

		if max_records_per_batch > 500 or max_records_per_batch < 0:
			raise ValueError("Maximum records per batch is 500")

		self.record_max_size = record_max_size
		self.batch_max_size = batch_max_size
		self.max_records_per_batch = max_records_per_batch

		if input_format not in ["string", "json"]:
			raise ValueError("{} is not allowed as a format, allowed values are string or json".format(input_format))

		self.input_format = input_format

	def is_too_large(self, record):
		'''
		Checks whether record in array is too large, against the defined record_max_size

		:param str/dict record: The record to check
		:returns: True or False
		:rtype: bool
		'''

		return self.get_record_size(record) > self.record_max_size

	def get_data(self, data):
		'''
		Iterate over the given array. If array item is too
		large (would go over Kinesis' record size limit), discard it.

		:param list data: an array of strings or dicts with format {'Data' : b'data', 'PartitionKey' : 'k'}
		:returns: iterator over array
		:rtype: iterator

		'''

		for d in data:

			if self.is_too_large(d):
				# Simply discard items that are too large
				print("WARNING: Discarding record going over size limit")
				continue

			yield d

		return

	def get_record_size(self, record):
		'''
		Return size of the given record. If records are in json format, 
		check that PartitionKey(Unicode string) and Data(bytes) together do not
		exceed the maximum payload size. If records are strings, we just
		check the size of the string.

		:param str/dict record: Record to check
		:returns: Size of record in bytes
		:rtype: int
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

		:param list data: An array to batch
		:returns: An iterator over the array, each iteration returning an optimal batch
		:rtype: iterator
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
				yield batch
				return

