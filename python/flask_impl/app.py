from flask import Flask, request, jsonify
import json
import xmltodict
import re
from http import HTTPStatus
from yangson import DataModel
from yangson.enumerations import ContentType


# Define constants for the URNs, namespace, and JSON keys
URN_ENCODING_JSON = "urn:ietf:capability:https-notif-receiver:encoding:json"
URN_ENCODING_XML = "urn:ietf:capability:https-notif-receiver:encoding:xml"
JSON_RECEIVER_CAPABILITIES = "receiver-capabilities"
JSON_RECEIVER_CAPABILITY = "receiver-capability"
UHTTPS_CONTENT_TYPE = 'Content-Type'
UHTTPS_ACCEPT = 'Accept'


# Define constants for media types
MIME_APPLICATION_XML = "application/xml"
MIME_APPLICATION_JSON = "application/json"

# collector capabilities
json_capable = True
xml_capable = True

# Define your YANG module path and model name
yang_dir_path = "../../yang_modules/" 
yang_library_path = "../../yang_modules/yang-library.json" 

app = Flask(__name__)

# Initialize the YANG data model
data_model = DataModel.from_file(yang_library_path,[yang_dir_path])

# Custom function to remove namespaces from XML keys
def strip_namespace(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            # Remove namespace prefix
            stripped_key = key.split(':')[-1] if ':' in key else key
            new_data[stripped_key] = strip_namespace(value)
        return new_data
    elif isinstance(data, list):
        return [strip_namespace(item) for item in data]
    else:
        return data

def validate_relay_notif(data_string):
    try:
        # Try to parse the data string as JSON
        json_data = json.loads(data_string)
    except json.JSONDecodeError:
        # If JSON parsing fails, assume the data is XML and parse it
        try:
            parsed_xml = xmltodict.parse(data_string, process_namespaces=True)
            parsed_xml = strip_namespace(parsed_xml)
            # Restructure
            json_data = {
                "ietf-https-notif:notification": {
                    "eventTime": parsed_xml["notification"]["eventTime"],
                    "event": parsed_xml["notification"]["event"]
                }
            }
        except Exception as e:
            return 0
            
    # Validate the parsed JSON data against the YANG model
    try:
        instance = data_model.from_raw(json_data)
        instance.validate(ctype=ContentType.all)
        return 1
    except Exception as e:
        return 0

def build_capabilities_data(json_capable, xml_capable):
    capabilities_data = []
    if json_capable:
        capabilities_data.append(URN_ENCODING_JSON)
    if xml_capable:
        capabilities_data.append(URN_ENCODING_XML)
    return capabilities_data

def build_xml(capabilities_data):
    """Builds an XML string from capabilities data."""
    xml_content = '<receiver-capabilities>'
    for capability in capabilities_data:
        xml_content += f'    <receiver-capability>{capability}</receiver-capability>\n'
    xml_content += '</receiver-capabilities>'
    return xml_content

def build_json(capabilities_data):
    """Builds a JSON structure from capabilities data."""
    return json.dumps({
        JSON_RECEIVER_CAPABILITIES: {
            JSON_RECEIVER_CAPABILITY: capabilities_data
        }
    }, indent=2)

def get_q_value(accept_header, media_type):
    """Extracts the q value for a specific media type from the Accept header."""
    pattern = re.compile(rf"{media_type}(;q=([0-9.]+))?")
    match = pattern.search(accept_header)
    if match:
        q_value = match.group(2)
        return float(q_value) if q_value else 1.0
    return 0.0

def get_default_response(json_capable, xml_capable, capabilities_data):
    """Returns the default response based on capabilities."""
    if xml_capable:
        return build_xml(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_XML}
    elif json_capable:
        return build_json(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_JSON}
    return jsonify({"error": "No valid capabilities found"}), HTTPStatus.INTERNAL_SERVER_ERROR

def respond_with_content_type(accept_header, json_capable, xml_capable, capabilities_data):
    """Responds based on the Accept header and content capabilities, considering q-values."""
    q_xml = get_q_value(accept_header, MIME_APPLICATION_XML)
    q_json = get_q_value(accept_header, MIME_APPLICATION_JSON)

    if q_xml < 0 or q_json < 0 or q_xml > 1 or q_json > 1: 
        return jsonify({"error": "Invalid q value"}), HTTPStatus.BAD_REQUEST

    if q_json == 0 and q_xml == 0:
        return get_default_response(json_capable, xml_capable, capabilities_data)

    if xml_capable and (q_xml >= q_json or not json_capable):
        return build_xml(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_XML}

    if json_capable and q_json > 0:
        return build_json(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_JSON}

    return jsonify({"error": "Not acceptable"}), HTTPStatus.NOT_ACCEPTABLE

@app.route('/capabilities', methods=['GET'])
def get_capabilities():
    """Handles the /capabilities GET request."""

    capabilities_data = build_capabilities_data(json_capable, xml_capable)

    accept_header = request.headers.get(UHTTPS_ACCEPT)
    if accept_header:
        return respond_with_content_type(accept_header, json_capable, xml_capable, capabilities_data)

    return get_default_response(json_capable, xml_capable, capabilities_data)

@app.route('/relay-notification', methods=['POST'])
def post_notification():
    # Get the Content-Type of the request
    req_content_type = request.headers.get(UHTTPS_CONTENT_TYPE)

    if req_content_type == None:
        return "Content-type is None -> Empty Body Notification", HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    # Check for XML content type and XML support
    if req_content_type == MIME_APPLICATION_XML:
        if not xml_capable:
            return "XML encoding not supported", HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    # Check for JSON content type and JSON support
    elif req_content_type == MIME_APPLICATION_JSON:
        if not json_capable:
            return "JSON encoding not supported", HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    # Unsupported Content-Type
    else:
        return "Unsupported Media Type", HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    # If the Content-Type is supported, respond with 204 No Content
    if validate_relay_notif(request.data):
        return '', HTTPStatus.NO_CONTENT
    else:
        return "relay notification doesn't correspond with the yang module", HTTPStatus.BAD_REQUEST

if __name__ == '__main__':
    app.run()  # Start HTTPS server with a self-signed certificate
