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

def big_array():
	f = open("tests/HSL_n_linjat.geojson", "rb")
	string_of_1_megabyte = f.read(1048576)
	string_of_less_than_1_megabyte = f.read(999999)
	string_of_a_lot_more = f.read(2000000)
	string_of_a_bit_more = f.read(1048579)
	return [string_of_1_megabyte, string_of_less_than_1_megabyte,string_of_a_lot_more,string_of_a_bit_more]

def oversize_array():
	f = open("tests/HSL_n_linjat.geojson", "rb")
	st = f.read(1048576)
	arr = [{'Data' : st, 'PartitionKey' : '1'}, 
			{'Data' : st, 'PartitionKey' : '2'},
			{'Data' : st, 'PartitionKey' : '3'},
			{'Data' : st, 'PartitionKey' : '4'},
			{'Data' : st, 'PartitionKey' : '5'},
			{'Data' : st, 'PartitionKey' : '6'}]
	return arr

if __name__ == "__main__":
	#arr = big_array()
	#print(len(arr[3]))
	#js = {'Data' : arr[3], 'PartitionKey' : '123'}
	#batch = [js]

	batch = oversize_array()
	response = client.put_records(
	 		    Records=batch,
	 		    StreamName='Tuikku-Dev-Stream'
	 		)
	print(response)

	# # Initialise batching code
	# batcher = KinesisBatcher(input_format="json", record_max_size=100, batch_max_size=500, max_records_per_batch=2)

	# while True:

	# 	records = get_random_sample_records()
	# 	print(records)
	# 	print("****")
	# 	for batch in batcher.batch_data(records):


	# 		print("Putting {} records to stream...".format(len(batch)))
	# 		response = client.put_records(
	# 		    Records=batch,
	# 		    StreamName='Tuikku-Dev-Stream'
	# 		)
	# 		print(response)

	# 		# Check for errors, possibly re-send items

	# 	time.sleep(5)

	# 		# Here you'd check for errors
	# 		# and possibly re-send 



