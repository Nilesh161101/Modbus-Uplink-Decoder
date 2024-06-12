#110a80090000410f04000300000000000fca0044815810 
#110A80090000411B07000F00000000000FCC8644816CBC00000000003FDA904582C5C3 

import struct

# Define the data type mapping
DATA_TYPE_MAPPING = {
    "UINT64": 16,  # 64 bits = 8 bytes, but represented as a hex string, so 16 characters
    "FLOAT32": 8   # 32 bits = 4 bytes, but represented as a hex string, so 8 characters
}

# Define the endpoint data types
ENDPOINT_DATA_TYPES = ["UINT64", "FLOAT32", "UINT64", "FLOAT32", "UINT64", "FLOAT32", "UINT64", "FLOAT32", "UINT64", "FLOAT32"]

def decode_uplink(uplink):
    # Extract different parts of the uplink string using fixed offsets
    endpoint = uplink[0:2]
    command_id = uplink[2:4]
    cluster_id = uplink[4:8]
    attribute_id = uplink[8:12]
    attribute_type = uplink[12:14]
    data_size = uplink[14:16]
    data_descriptor = uplink[16:22]
    data_start = 22

    # Validate the extracted parts against expected values
    if endpoint != "11":
        return "Invalid endpoint"

    if command_id.lower() != "0a":
        return "Invalid CommandID"

    if cluster_id != "8009":
        return "Invalid ClusterID"

    if attribute_id != "0000":
        return "Invalid AttributeID"

    if attribute_type != "41":
        return "Invalid Attribute type"

    # Break down the data descriptor into bytes
    descriptor_bytes = [data_descriptor[i:i+2] for i in range(0, 6, 2)]
    # Convert the descriptor bytes into a single integer
    descriptor_int = int(''.join(descriptor_bytes), 16)

    # Extract the last 10 bits
    last_10_bits = descriptor_int & 0x3FF  # 0x3FF is binary 1111111111
    print("Data Descriptor (last 10 bits):", format(last_10_bits, '010b'))

    # Check which endpoints are present based on the last 10 bits
    endpoints_present = []
    for i in range(10):
        if last_10_bits & (1 << i):
            endpoints_present.append(i)

    print("Endpoints present:", endpoints_present)

    # Extract data values from the uplink based on the endpoint presence
    extracted_values = []
    data_offset = data_start

    for i in range(10):
        data_type = ENDPOINT_DATA_TYPES[i]
        data_length = DATA_TYPE_MAPPING[data_type]

        if i in endpoints_present:
            data = uplink[data_offset:data_offset + data_length]
            value = extract_data_value(data, data_type)
            if isinstance(value, str):  # Error check for extract_data_value
                return value
            extracted_values.append((f"Endpoint {i}", value))
        else:
            extracted_values.append((f"Endpoint {i}", "Not Present"))

        # Move the data offset to the next segment
        data_offset += data_length

    return extracted_values

def extract_data_value(data, data_type):
    try:
        if data_type == "UINT64":
            # Convert hex string to an integer
            value = int(data, 16)
            return value
        elif data_type == "FLOAT32":
            # Convert hex string to a 32-bit floating-point number
            value = struct.unpack('>f', bytes.fromhex(data))[0]
            return value
        else:
            return "Invalid data type"
    except (ValueError, struct.error):
        return "Error decoding data"

while True:
    # Prompt the user to enter the uplink string
    uplink = input("Please enter the uplink: ")
    # Decode the uplink and get the result
    result = decode_uplink(uplink)
    if isinstance(result, list):
        # Print the decoded values if successful
        for endpoint, value in result:
            print(f"{endpoint}: {value}")
    else:
        # Print the error message if decoding failed
        print(result)
    # Ask if the user wants to continue decoding
    cont = input("Wish to continue decoding? (YES/NO): ")
    if cont.upper() != "YES":
        break

