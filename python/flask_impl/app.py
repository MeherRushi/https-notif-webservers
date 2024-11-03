from flask import Flask, request, jsonify, Response
import json
import xml.etree.ElementTree as ET
import subprocess
import re

# Define constants for the URNs, namespace, and JSON keys
NAMESPACE = "urn:ietf:params:xml:ns:yang:example"
URN_ENCODING_JSON = "urn:ietf:capability:https-notif-receiver:encoding:json"
URN_ENCODING_XML = "urn:ietf:capability:https-notif-receiver:encoding:xml"
JSON_RECEIVER_CAPABILITIES = "receiver-capabilities"
JSON_RECEIVER_CAPABILITY = "receiver-capability"



app = Flask(__name__)

def read_data_set_server_capabilities(data_file_path):
    # Initialize capability flags
    json_capable = False
    xml_capable = False

    # Check the file extension to determine parsing method
    if data_file_path.endswith('.xml'):
        json_capable, xml_capable = parse_xml_capabilities(data_file_path)
    elif data_file_path.endswith('.json'):
        json_capable, xml_capable = parse_json_capabilities(data_file_path)

    return json_capable, xml_capable

def parse_xml_capabilities(data_file_path):
    # Initialize capability flags
    json_capable = False
    xml_capable = False

    # Parse the XML file
    tree = ET.parse(data_file_path)
    root = tree.getroot()

    # Iterate through receiver-capabilities elements
    for capability in root.findall(f'{{{NAMESPACE}}}receiver-capabilities'):
        receiver_capability = capability.find(f'{{{NAMESPACE}}}receiver-capability')

        if receiver_capability is not None:
            capability_value = receiver_capability.text
            if capability_value == URN_ENCODING_JSON:
                json_capable = True
            elif capability_value == URN_ENCODING_XML:
                xml_capable = True

    return json_capable, xml_capable

def parse_json_capabilities(data_file_path):
    # Initialize capability flags
    json_capable = False
    xml_capable = False

    # Read and parse the JSON file
    with open(data_file_path, 'r') as json_file:
        data = json.load(json_file)

        # Navigate through the JSON structure
        receiver_capabilities = data.get(JSON_RECEIVER_CAPABILITIES, {})
        capabilities = receiver_capabilities.get(JSON_RECEIVER_CAPABILITY, [])

        for capability_value in capabilities:
            if capability_value == URN_ENCODING_JSON:
                json_capable = True
            elif capability_value == URN_ENCODING_XML:
                xml_capable = True

    return json_capable, xml_capable

def call_c_program(data_file_path, yang_model_path):
    # Call the C program using subprocess
    result = subprocess.run(
        ["./yang_validate", data_file_path, yang_model_path],
        capture_output=True,  # Capture standard output and error
        text=True             # Return output as string (text)
    )

    # Print the output from the C program
    print("C Program Output:")
    print(result.stdout)  # Output from the C program
    print(result.stderr)   # Error output (if any)

    # Check the return code to determine success or failure
    if result.returncode == 0:
        print("C program executed successfully.")
        return True
    else:
        print(f"C program failed with return code: {result.returncode}")
        return False

# Define constants for media types
MIME_APPLICATION_XML = "application/xml"
MIME_APPLICATION_JSON = "application/json"
MIME_ALL = "*/*"

def get_q_value(accept_header, media_type):
    """Extracts the q value for a specific media type from the Accept header."""
    pattern = re.compile(rf"{media_type}(;q=([0-9.]+))?")
    match = pattern.search(accept_header)
    if match:
        q_value = match.group(2)
        return float(q_value) if q_value else 1.0
    return 0.0

def get_default_response(json_capable, xml_capable):
    """Return the default response based on capabilities."""
    if xml_capable:
        return "<data>Your XML response here</data>", 200, {'Content-Type': MIME_APPLICATION_XML}
    elif json_capable:
        return jsonify({"data": "Your JSON response here"}), 200
    return jsonify({"error": "No valid capabilities found"}), 500

def respond_with_content_type(accept_header, json_capable, xml_capable):
    """Respond based on the Accept header and content capabilities considering q-values, prioritizing XML."""
    q_xml = get_q_value(accept_header, MIME_APPLICATION_XML)
    q_json = get_q_value(accept_header, MIME_APPLICATION_JSON)

    # If both q values are zero, default to XML
    if q_json == 0 and q_xml == 0:
        return get_default_response(json_capable, xml_capable)

    # Prefer XML if available and has a higher or equal q value
    if xml_capable and (q_xml >= q_json or not json_capable):
        return "<data>Your XML response here</data>", 200, {'Content-Type': MIME_APPLICATION_XML}

    # If JSON is preferred, check if it's capable
    if json_capable and q_json > 0:
        return jsonify({"data": "Your JSON response here"}), 200

    return jsonify({"error": "Not acceptable"}), 406

@app.route('/capabilities', methods=['GET'])
def get_capabilities():
    # Check the Accept header
    data_file_path = "example-config.xml"  #make it configurable as input 
    yang_model_path = "example.yang"    #make it configurable as input 

    yang_valid = call_c_program(data_file_path, yang_model_path)

    if yang_valid:
        # the data in the datastore is valid
        json_capable,xml_capable = read_data_set_server_capabilities(data_file_path)
    else:
        # internal server error as the capabilities are not 
        # corresponding to the YANG data model
        return jsonify({"error": "Internal error, incorrect data in the datastore"}), 500


    print(f"DEBUG: json_capabale: {json_capable}, xml_capable:{xml_capable} ")
    accept_header = request.headers.get('Accept')
    print(f"DEBUG: Accept header: {accept_header}")

    if accept_header:
        return respond_with_content_type(accept_header, json_capable, xml_capable)

    # If no Accept header is provided, return the default response
    return get_default_response(json_capable, xml_capable)


if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # Start HTTPS server with a self-signed certificate
