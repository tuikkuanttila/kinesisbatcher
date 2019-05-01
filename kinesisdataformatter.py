# This module has helper functions to format data into Kinesis


# Constraints:
# 
# Takes in an array of arrays
# Returns an array of arrays
# Max size of output array 1 MB
# Max size of output batch is 5 MB
# maximum number of records in an output batch is 500
# 



# Arrays sent in the same order as they are received
# So we have to monitor the size and count of the batch continuously
# We have to look maybe if adding the next record to the batch would cause
# for the size to be too large

# If they are sent to AWS there's an issue that sending of a record in the
# batch could fail and then the result would no longer be in the same order..

ALLOWED_FORMATTING_VALUES = ["string", "json"]


class KinesisBatcher:


	# TODO should we keep track of almost filled records for optimizing?
	# No because then they would not stay in the same order

	def __init__(self, record_max_size=10, batch_max_size=50, max_records_per_batch=5, formatting="string"):
		self.unmodified_data = []
		self.record_max_size = record_max_size
		self.batch_max_size = batch_max_size
		self.max_records_per_batch = max_records_per_batch
		self.discarded = 0

		if formatting not in ALLOWED_FORMATTING_VALUES:
			raise ValueError("{} is not allowed as a format, allowed values are {}".format(formatting, ALLOWED_FORMATTING_VALUES))

		self.format = formatting

	def is_too_large(self, record):

		return self.get_record_size(record) > self.record_max_size

	def get_data(self, data):

		for d in data:
			print("Now getting next item")
			print(d)

			#if not isinstance(d, str):
			#	self.nonstring += 1
			#	continue

			if self.is_too_large(d):
				# Simply discard items that are too large
				self.discarded += 1
				continue

			yield d

		return

	def get_record_size(self, record):
		

		if self.format == "json":
			try:
				return len(record["Data"]) + len(record["PartitionKey"].encode("utf-8"))
			except KeyError:
				raise ValueError("Record {} was invalid json for Kinesis".format(record))
			except AttributeError:
				raise ValueError("Record {} invalid; Expected partition key to be string, data bytes".format(record))

		elif self.format == "string":
			return len(record.encode("utf-8"))

	def batch_data(self, data):
		print("Starting batch operations...")
		batch = []
		print(data)

		data_for_batch = self.get_data(data)
		current_batch_size = 0
		current_records_in_batch = 0

		while True:

			try:

				print("Getting item from iterator...")
				next_item = next(data_for_batch)
				print(next_item)
				if current_batch_size + self.get_record_size(next_item) > self.batch_max_size or current_records_in_batch == self.max_records_per_batch:
					# This batch couldn't fit any more items, so return it
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


if __name__ == "__main__":

	batcher = KinesisBatcher(["i", 2, "ii", "iii", "i", "i", "iw", "iasda", "a"])
	iterator = batcher.batch_data()
	print(next(iterator))
	print(next(iterator))

	## Instead of initialising with data
	# should we batcher = KinesisBatcher(maxdata=1)
	# batcher.batch(["a", "b", "c"])
	# for data in batcher.batch(["a", "b", "c"])

