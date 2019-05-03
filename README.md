# KinesisBatcher

A library for splitting arrays into batches suitable for AWS Kinesis,
though you can use it for any other purpose too. 

## Background

Each request to write to Kinesis, using the PutRecords operation,
can support up to 500 records. Each record in the request can be 
as large as 1 MiB, up to a limit of 5 MiB for the entire request, 
including the partition keys. [1]

KinesisBatcher takes care of splitting your data into optimal batches
for Kinesis writes while keeping the records in order. 
It forms batches that are suitably sized and
discards records that go over the 1 MiB limit.

## Installation

pip install git+https://github.com/tuikkuanttila/batcher.git

## Usage

To use the batcher, you first create an instance of KinesisBatcher
and then call the batch_data method on it with your data. You can
specify if your data is in string or json (dict) format. Default
is string.
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

A complete example on how to use KinesisBatcher with boto3 is below. Note
that boto3 is not included with the library. You can install it via pip:
`pip install boto3`

~~~
import boto3
import random
import time

from batcher import KinesisBatcher


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
	batcher = KinesisBatcher(formatting="json", record_max_size=100, batch_max_size=500, max_records_per_batch=2)

	while True:

		records = get_random_sample_records()

		for batch in batcher.batch_data(records):

			print("Putting {} records to stream...".format(len(batch)))
			response = client.put_records(
			    Records=batch,
			    StreamName='your-stream-name'
			)
			print(response)

			# Check for errors, possibly re-send items

		time.sleep(5)

~~~

You can also define the batch limits yourself if that fits your use case, 
in case you want smaller batches for example. For more details, see docs/docs.rst.
















[1] https://docs.aws.amazon.com/kinesis/latest/APIReference/API_PutRecords.html