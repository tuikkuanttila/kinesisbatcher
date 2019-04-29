import boto3

client = boto3.client('kinesis')


if __name__ == "__main__":

	records = []
	for i in range(10):
		data = "this is record number " + str(i)
		record = {'Data' : data, 'PartitionKey' : 'testRecords'}
		records.append(record)

	print("Putting records to stream...")
	response = client.put_records(
	    Records=records,
	    StreamName='Tuikku-Dev-Stream'
	)
	print(response)

