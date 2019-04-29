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



class KinesisBatcher:
	# TODO should we keep track of almost filled records for optimizing?
	# No because then they would not stay in the same order

	def __init__(self, data, record_max_size=10, batch_max_size=50, max_records_per_batch=5):
		self.unmodified_data = data
		self.record_max_size = record_max_size
		self.batch_max_size = batch_max_size
		self.max_records_per_batch = max_records_per_batch
		self.discarded = 0

	def is_too_large(self, record):

		return len(record) > self.record_max_size

	def get_data(self):
		for d in self.unmodified_data:
			if self.is_too_large(d):
				# Simply discard items that are too large
				self.discarded += 1
				continue
			yield d
		return

	def get_batch_size(self, batch):
		# TODO return sum of records in bytes
		# TODO keep track of sum somewhere else instead
		# of returning it here
		return len(batch)

	def get_record_size(self, record):
		# TODO return size in bytes 
		return len(record)

	def batch_data(self):

		batch = []
		data_for_batch = self.get_data()

		while True:

			try:

				next_item = next(data_for_batch)

				if self.get_batch_size(batch) + self.get_record_size(next_item) > self.batch_max_size or len(batch) > self.max_records_per_batch:
					yield batch
					batch = []
				batch.append(next_item)

			except StopIteration:

				print("All data batched")
				print("Discarded {} items that went over the max record size limit of {}".format(self.discarded, self.batch_max_size))

				return


if __name__ == "__main__":

	batcher = KinesisBatcher(["i", "ii", "iii", "i", "i", "iw", "iasda", "a"])
	iterator = batcher.batch_data()
	print(next(iterator))



