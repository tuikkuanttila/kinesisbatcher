class KinesisBatcher(formatting="string", record_max_size=10, batch_max_size=50, max_records_per_batch=5)

Create a new KinesisBatcher.
Parameters

formatting(string) The type of data to batch. You can either specify json or string.
If you specify "json", batch_data will expect an array of dicts {'Data' : b'data', 'PartitionKey' : 'string'}.
If you specify string, batch_data will expect an array of strings.

record_max_size Maximum sixe of one record (array element) in bytes. Default 1000000, AWS Kinesis limit.

batch_max_size Maximum size of batch (array of records). Default 5000000, AWS Kinesis limit.

max_records_per_batch Maximum records per batch (array of records). Default 500, AWS Kinesis limit.

discarded Count of discarded items

is_too_large(self, record):

Returns False if record is over record_max_size, otherwise True

get_data(self, data)

Returns an iterator over the array data. Records that are too large are discarded.

get_record_size(self, record)

Return size of the given record in bytes. If records are in json format, 
returns sum of PartitionKey(Unicode string) and Data(bytes). If records are strings,
returns the size of the string.


batch_data(self, data)
Batches the given data according to KinesisBatcher's constraints. Returns an iterator over the batches,
that is, each iteration returns a batch (an array).
