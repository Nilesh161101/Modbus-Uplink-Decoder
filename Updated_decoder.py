import struct

# Prompt the user to input the number of endpoints in the message frame
try:
    number_of_endpoints = int(input("Please enter the number of endpoints present in the message frame:"))
except ValueError:
    # If the input is not a valid integer, print an error message and exit
    print("Invalid input. Please enter an integer.")
    exit(1)

# Depending on the number of endpoints, ask the user for the data types
if number_of_endpoints == 2:
    endpoint0_type = input("Data Type for endpoint 0:")
    endpoint1_type = input("Data Type for endpoint 1:")
elif number_of_endpoints == 1:
    endpoint0_type = input("Data Type for endpoint 0:")
    endpoint1_type = None
else:
    # If the number of endpoints is not 1 or 2, print an error message and exit
    print("Only 1 or 2 endpoints can be read currently")
    exit(1)

# Function to decode the uplink message
def decode_uplink(uplink):
    # Extract various parts of the uplink message
    endpoint = uplink[0:2]
    command_id = uplink[2:4]
    cluster_id = uplink[4:8]
    attribute_id = uplink[8:12]
    attribute_type = uplink[12:14]
    data_size = uplink[14:16]
    data_descriptor = uplink[16:22]
    data = uplink[22:]

    # Validate the extracted parts against expected values
    if endpoint not in ["11"]:
        return "Invalid endpoint"
    if command_id != "0a":
        return "Invalid CommandID"
    if cluster_id != "8009":
        return "Invalid ClusterID"
    if attribute_id != "0000":
        return "Invalid AttributeID"
    if attribute_type != "41":
        return "Invalid Attribute type"

    # Depending on the number of endpoints, extract and decode the data
    if number_of_endpoints == 2:
        # For 2 endpoints, extract and decode data for both
        data_endpoint0 = data[:16]  # assuming 8 bytes for UINT64
        data_endpoint1 = data[16:24]  # assuming 4 bytes for FLOAT32
        data_endpoint0_value = extract_data_value(data_endpoint0, endpoint0_type)
        data_endpoint1_value = extract_data_value(data_endpoint1, endpoint1_type)
        return data_endpoint0_value, data_endpoint1_value
    elif number_of_endpoints == 1:
        # For 1 endpoint, extract and decode data for endpoint 0
        data_endpoint0 = data[:16]  # assuming 8 bytes for UINT64
        data_endpoint0_value = extract_data_value(data_endpoint0, endpoint0_type)
        return data_endpoint0_value, None
    else:
        # If number of endpoints is not supported, return an error
        return "Unsupported number of endpoints"

# Function to extract the value from the data based on its type
def extract_data_value(data, data_type):
    if data_type == "UINT64":
        # Convert hexadecimal string to integer
        value = int(data, 16)
        return value
    elif data_type == "FLOAT32":
        # Convert hexadecimal string to float
        value = struct.unpack('>f', bytes.fromhex(data))[0]
        return value
    else:
        # Return an error message if the data type is invalid
        return "Invalid data type"

# Loop to continuously prompt for uplink messages and decode them
while True:
    payload = input("Please enter the uplink: ")
    register_values = decode_uplink(payload)
    if number_of_endpoints == 2:
        register_value_endpoint0, register_value_endpoint1 = register_values
        print("Register value Endpoint 0:", register_value_endpoint0)
        print("Register value Endpoint 1:", register_value_endpoint1)
    elif number_of_endpoints == 1:
        register_value_endpoint0 = register_values
        print("Register value Endpoint 0:", register_value_endpoint0)

    # Ask the user if they want to continue decoding
    cont = input("Wish to continue decoding? (YES/NO): ")
    if cont.upper() != "YES":
        break

