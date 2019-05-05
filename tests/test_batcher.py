'''
Tests for KinesisBatcher
'''
import json
import string

import pytest

from kinesisbatcher import KinesisBatcher

@pytest.fixture(scope="module")
def kinesisbatcher_string():
	''' 
	Create a common KinesisBatcher instance for test functions
	'''
	return KinesisBatcher(input_format="string")


@pytest.fixture(scope="module")
def kinesisbatcher_json():
	''' 
	Create a common KinesisBatcher instance for test functions
	'''
	return KinesisBatcher(input_format="json")

@pytest.fixture(scope="module")
def large_string_array():
	'''
	Get a test array (geojson featurecollection) of 1199 bus line geometries in Helsinki,
	in total approximately 27 MB. At item 237,
	we go over the 5 MB limit.
	'''
	records = []
	with open("tests/HSL_n_linjat.geojson", "rb") as too_large_geojson:
		geojson = json.load(too_large_geojson)
		for feat in geojson["features"]:
			records.append(json.dumps(feat))
	return records

@pytest.fixture(scope="module")
def large_json_array():
	records = []
	with open("tests/HSL_n_linjat.geojson", "rb") as too_large_geojson:
		geojson = json.load(too_large_geojson)
		for feat in geojson["features"]:
			records.append({'PartitionKey' : feat["properties"]["NUMERO"], 'Data' : json.dumps(feat)})
	return records

@pytest.fixture(scope="module")
def array_of_strings():
	f = open("tests/HSL_n_linjat.geojson", "rb")
	string_of_1_megabyte = f.read(1048576)
	string_of_more_than_1_megabyte = f.read(1048577)
	f.close()
	return [string_of_1_megabyte.decode('utf-8'), string_of_more_than_1_megabyte.decode('utf-8')]

@pytest.fixture(scope="module")
def array_of_jsons():
	f = open("tests/HSL_n_linjat.geojson", "rb")
	string_of_1_megabyte = f.read(1048576)
	string_of_less_than_1_megabyte = f.read(1048573)
	f.close()
	arr = [{'Data' : string_of_1_megabyte, 'PartitionKey' : 'This record will fail'},
			{'Data' : string_of_less_than_1_megabyte, 'PartitionKey' : 'This record will fail because of key and data together'},
			{'Data' : string_of_less_than_1_megabyte, 'PartitionKey' : 'Ok'}]
	return arr

@pytest.fixture(scope="module")
def small_array_of_strings():
	f = open("tests/HSL_n_linjat.geojson", "rb")
	small_string = f.read(1000).decode('utf-8')
	f.close()
	return [small_string for i in range(1000)]

def test_json_formatting(kinesisbatcher_json):
	'''
	If the given json does not include 'Data' property, we
	should raise ValueError
	'''
	incorrect_json_array = [{'mydata' : 'some data', 'PartitionKey' : 123}]
	with pytest.raises(ValueError) as excinfo:
		for b in kinesisbatcher_json.batch_data(incorrect_json_array):
			print(b)
	assert "invalid json for Kinesis" in str(excinfo.value)


def test_splitting_stringarray(kinesisbatcher_string, large_string_array):
	''' 
	One batch should not be larger than 5 MB. 
	We know that our test array reaches that
	limit after record 236 so the first batch should have
	236 records

	'''
	b = next(kinesisbatcher_string.batch_data(large_string_array))

	assert len(b) == 236

def test_splitting_jsonarray(kinesisbatcher_json, large_json_array):
	''' 
	One batch should not be larger than 5 MB. 
	We know that our test array reaches that
	limit after record 236 so the first batch should have
	236 records

	'''
	b = next(kinesisbatcher_json.batch_data(large_json_array))

	assert len(b) == 236

def test_large_strings(kinesisbatcher_string, array_of_strings):
	'''
	Check that the over 1 MB string gets discarded
	'''
	b = next(kinesisbatcher_string.batch_data(array_of_strings))

	assert len(b) == 1
	assert len(b[0]) == 1048576

def test_large_json(kinesisbatcher_json, array_of_jsons):
	'''
	Check that the two over 1 MB items get discarded
	and the one left is the one where data and key
	together are less than 1 MB
	'''
	b = next(kinesisbatcher_json.batch_data(array_of_jsons))

	assert len(b) == 1
	assert b[0]['PartitionKey'] == 'Ok'

def test_splitting_stringarray_by_count(kinesisbatcher_string, small_array_of_strings):
	'''
	Test array has 1000 small items. Check that first batch returned has 500
	'''
	b = next(kinesisbatcher_string.batch_data(small_array_of_strings))

	assert len(b) == 500

def test_ordering_of_array(kinesisbatcher_string):
	'''
	Test that batching returns the array in the order
	it was given
	'''
	test_array = ["first", "second", "third", "fourth"]
	b = next(kinesisbatcher_string.batch_data(test_array))

	assert b[0] == "first"
	assert b[1] == "second"
	assert b[2] == "third"
	assert b[3] == "fourth"

def test_invalid_initialization():

	with pytest.raises(ValueError) as excinfo:
		batcher = KinesisBatcher(input_format="xml")
	assert "is not allowed as a format" in str(excinfo.value)

	with pytest.raises(ValueError) as excinfo:
		batcher = KinesisBatcher(record_max_size=10000000)
	assert "Maximum record size is 1048576 bytes" in str(excinfo.value)

	with pytest.raises(ValueError) as excinfo:
		batcher = KinesisBatcher(batch_max_size=10000000)
	assert "Maximum batch size is 5242880 bytes" in str(excinfo.value)

	with pytest.raises(ValueError) as excinfo:
		batcher = KinesisBatcher(max_records_per_batch=10000000)
	assert "Maximum records per batch is 500" in str(excinfo.value)						







