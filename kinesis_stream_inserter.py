import boto3
import random
import time

from kinesisbatcher import KinesisBatcher


client = boto3.client('kinesis')


def get_random_sample_records():

	records = []

	for i in range(random.randint(1, 5)):

		partition_key = "partition-{}".format(i)
		record = {'Data' : b'a string', 'PartitionKey' : partition_key}
		records.append(record)

	return records

if __name__ == "__main__":

	# Initialise batching code
	batcher = KinesisBatcher(input_format="json", record_max_size=100, batch_max_size=500, max_records_per_batch=2)

	while True:

		records = get_random_sample_records()
		print(records)
		print("****")
		for batch in batcher.batch_data(records):


			print("Putting {} records to stream...".format(len(batch)))
			response = client.put_records(
			    Records=batch,
			    StreamName='Tuikku-Dev-Stream'
			)
			print(response)

			# Check for errors, possibly re-send items

		time.sleep(5)

			# Here you'd check for errors
			# and possibly re-send 



	# records = []
	# for i in range(10):
	# 	data = "this is record number " + str(i)
	# 	record = {'Data' : data, 'PartitionKey' : 'testRecords'}
	# 	records.append(record)

