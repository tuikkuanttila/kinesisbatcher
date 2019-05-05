# KinesisBatcher

A library for splitting arrays into batches suitable for AWS Kinesis,
though you can use it for any other purpose too. 

## Background

Each request to write to Kinesis, using the PutRecords operation,
can support up to 500 records. Each record in the request can be 
as large as 1 MiB, up to a limit of 5 MiB for the entire request, 
including the partition keys. [1]

KinesisBatcher takes care of splitting your data into optimal batches
for Kinesis writes while keeping the records in order and unmodified. 
It forms batches that are suitably sized and
discards records that go over the 1 MiB limit.

## Installation

Using Pip:

pip install git+https://github.com/tuikkuanttila/kinesisbatcher.git#egg=kinesisbatcher

Tested with Python 3.7, may work with earlier versions of Python 3 as well. 

## Usage

To use the batcher, you first create an instance of KinesisBatcher
and then call the batch_data method on it with your data. The method
returns an iterator where each iteration returns a Kinesis-sized batch.
You can specify if your data is in string or in the json format expected by
Boto3. Default is string.
~~~
batcher = KinesisBatcher()
~~~
To specify json format
~~~
batcher = KinesisBatcher(input_format="json")
~~~
This will expect the array to be batched to consist of dicts of
type `{'Data' : b'data', 'PartitionKey' : string}`.

Then, batch your data! The batch_data method of KinesisBatcher takes
an array of records and returns an iterator over the batches.

~~~
for batcher in batcher.batch_data(records):
	put_records_to_stream(records)
~~~

## Examples

### Example with string array
~~~

import json
from kinesisbatcher import KinesisBatcher

def large_array():
	# Generate test data from Helsinki region transit lines from https://www.avoindata.fi/data/en_GB/dataset/hsl-n-linjat
	array = []
	with open("tests/HSL_n_linjat.geojson", "rb") as f:
		file_as_json = json.load(f)
		for feat in file_as_json["features"]:
			record = json.dumps(feat)
			array.append(record)
	return array

def send_to_kinesis(batch):

	# Your own implementation
	pass

if __name__ == "__main__":

	# 1199 items in array
	array = large_array()
	batcher = KinesisBatcher()

	for batch in batcher.batch_data(array):
		# batches are up to 500 items, up to 5 MB, individual records
		# up to 1 MB in size
		assert len(batch) <= 500
		assert sum([len(record) for record in batch]) <= 5242880
		assert len([x for x in batch if len(x) > 1048576]) == 0

		# Now you could put this batch to Kinesis etc 
		send_to_kinesis(batch)




~~~

### Example with boto3
A complete example on how to use KinesisBatcher with boto3 is below. Note
that boto3 is not included with the library. You can install it via pip:
`pip install boto3`

~~~
import boto3
import random
import time

from kinesisbatcher import KinesisBatcher


client = boto3.client('kinesis')


def get_random_sample_records():

	records = []

	for i in range(random.randint(1, 500)):

		partition_key = "partition-{}".format(i)
		record = {'Data' : b'a string', 'PartitionKey' : partition_key}
		records.append(record)

	return records

if __name__ == "__main__":

	batcher = KinesisBatcher(input_format="json")

	while True:

		records = get_random_sample_records()

		for batch in batcher.batch_data(records):

			print("Putting {} records to stream...".format(len(batch)))
			response = client.put_records(
			    Records=batch,
			    StreamName='your-stream-name'
			)
			print(response)

			# Check for errors in response['FailedRecordCount'] and possibly re-send items

		time.sleep(5)

~~~

For more details, see the module documentation in doc/kinesisbatcher.html

## Upcoming in the next version

Inform the user on which records were discarded.


















[1] https://docs.aws.amazon.com/kinesis/latest/APIReference/API_PutRecords.html