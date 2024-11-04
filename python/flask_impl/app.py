from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response
import json
import xml.etree.ElementTree as ET
import subprocess
import re
from http import HTTPStatus

# Define constants for the URNs, namespace, and JSON keys
NAMESPACE = "urn:ietf:params:xml:ns:yang:example"
URN_ENCODING_JSON = "urn:ietf:capability:https-notif-receiver:encoding:json"
URN_ENCODING_XML = "urn:ietf:capability:https-notif-receiver:encoding:xml"
JSON_RECEIVER_CAPABILITIES = "receiver-capabilities"
JSON_RECEIVER_CAPABILITY = "receiver-capability"
UHTTPS_CONTENT_TYPE = 'Content-Type'
UHTTPS_ACCEPT = 'Accept'

# Define constants for media types
MIME_APPLICATION_XML = "application/xml"
MIME_APPLICATION_JSON = "application/json"

# Define file paths
data_file_path = "../../get_yang_files_and_validators/example-config.xml"  # Make this configurable
yang_model_path = "../../get_yang_files_and_validators/example.yang"         # Make this configurable

app = FastAPI()

def read_data_set_server_capabilities(data_file_path):
    """Reads server capabilities from the given data file, returning capability flags and data."""
    if data_file_path.endswith('.xml'):
        return parse_xml_capabilities(data_file_path)
    elif data_file_path.endswith('.json'):
        return parse_json_capabilities(data_file_path)
    return False, False, []

def parse_xml_capabilities(data_file_path):
    """Parses XML capabilities from the provided file path."""
    capabilities_data = []
    tree = ET.parse(data_file_path)
    root = tree.getroot()

    for capability in root.findall(f'{{{NAMESPACE}}}receiver-capabilities'):
        receiver_capability = capability.find(f'{{{NAMESPACE}}}receiver-capability')
        if receiver_capability is not None:
            capability_value = receiver_capability.text
            capabilities_data.append(capability_value)
    
    json_capable = URN_ENCODING_JSON in capabilities_data
    xml_capable = URN_ENCODING_XML in capabilities_data

    return json_capable, xml_capable, capabilities_data

def parse_json_capabilities(data_file_path):
    """Parses JSON capabilities from the provided file path."""
    capabilities_data = []
    
    with open(data_file_path, 'r') as json_file:
        data = json.load(json_file)
        receiver_capabilities = data.get(JSON_RECEIVER_CAPABILITIES, {})
        capabilities = receiver_capabilities.get(JSON_RECEIVER_CAPABILITY, [])
        
        capabilities_data.extend(capabilities)
    
    json_capable = URN_ENCODING_JSON in capabilities_data
    xml_capable = URN_ENCODING_XML in capabilities_data

    return json_capable, xml_capable, capabilities_data

def build_xml(capabilities_data):
    """Builds an XML string from capabilities data."""
    xml_content = f'<capabilities xmlns="{NAMESPACE}">\n'
    for capability in capabilities_data:
        xml_content += f'  <receiver-capabilities>\n'
        xml_content += f'    <receiver-capability>{capability}</receiver-capability>\n'
        xml_content += f'  </receiver-capabilities>\n'
    xml_content += '</capabilities>'
    return xml_content

def build_json(capabilities_data):
    """Builds a JSON structure from capabilities data."""
    return json.dumps({
        JSON_RECEIVER_CAPABILITIES: {
            JSON_RECEIVER_CAPABILITY: capabilities_data
        }
    }, indent=2)

def call_c_program(data_file_path, yang_model_path):
    """Calls the C program to validate the YANG model against the data file."""
    result = subprocess.run(
        ["../../get_yang_files_and_validators/yang_validate", data_file_path, yang_model_path],
        capture_output=True,
        text=True
    )

    print("C Program Output:")
    print(result.stdout)
    print(result.stderr)

    return result.returncode == 0

def get_q_value(accept_header, media_type):
    """Extracts the q value for a specific media type from the Accept header."""
    pattern = re.compile(rf"{media_type}(;q=([0-9.]+))?")
    match = pattern.search(accept_header)
    if match:
        q_value = match.group(2)
        return float(q_value) if q_value else 1.0
    return 0.0

def get_default_response(json_capable, xml_capable, capabilities_data):
    """Returns the default response based on capabilities.
    If the desired header field is not present, the server can choose the format it prefers
    reference link : https://stackoverflow.com/questions/51006471/accept-header-in-http-request"""
    if xml_capable:
        return Response(content=build_xml(capabilities_data), media_type=MIME_APPLICATION_XML, status_code=HTTPStatus.OK)
    elif json_capable:
        return JSONResponse(content=json.loads(build_json(capabilities_data)), status_code=HTTPStatus.OK)
    return JSONResponse(content={"error": "No valid capabilities found"}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

def respond_with_content_type(accept_header, json_capable, xml_capable, capabilities_data):
    """Responds based on the Accept header and content capabilities, considering q-values."""
    q_xml = get_q_value(accept_header, MIME_APPLICATION_XML)
    q_json = get_q_value(accept_header, MIME_APPLICATION_JSON)

    if q_xml < 0 or q_json < 0 or q_xml > 1 or q_json > 1: 
        return JSONResponse(content={"error": "Invalid q value"}, status_code=HTTPStatus.BAD_REQUEST)

    if q_json == 0 and q_xml == 0:
        return get_default_response(json_capable, xml_capable, capabilities_data)

    if xml_capable and (q_xml >= q_json or not json_capable):
        return Response(content=build_xml(capabilities_data), media_type=MIME_APPLICATION_XML, status_code=HTTPStatus.OK)

    if json_capable and q_json > 0:
        return JSONResponse(content=json.loads(build_json(capabilities_data)), status_code=HTTPStatus.OK)

    return JSONResponse(content={"error": "Not acceptable"}, status_code=HTTPStatus.NOT_ACCEPTABLE)

@app.get("/capabilities")
async def get_capabilities(request: Request):
    """Handles the /capabilities GET request."""
    if call_c_program(data_file_path, yang_model_path):
        json_capable, xml_capable, capabilities_data = read_data_set_server_capabilities(data_file_path)
    else:
        raise HTTPException(status_code=500, detail="Internal error, incorrect data in the datastore")

    accept_header = request.headers.get(UHTTPS_ACCEPT)  # Retrieve the Accept header
    if accept_header:
        return respond_with_content_type(accept_header, json_capable, xml_capable, capabilities_data)

    return get_default_response(json_capable, xml_capable, capabilities_data)

@app.post("/relay-notification")
async def post_notification(request: Request):
    """Handles the /relay-notification POST request."""
    req_content_type = request.headers.get(UHTTPS_CONTENT_TYPE)
    response_content_type = None

    json_capable, xml_capable, _ = read_data_set_server_capabilities(data_file_path)

    # Check for XML content type and XML support
    if req_content_type == MIME_APPLICATION_XML:
        response_content_type = MIME_APPLICATION_XML
        if not xml_capable:
            return JSONResponse(content={"error": "XML encoding not supported"}, status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    # Check for JSON content type and JSON support
    elif req_content_type == MIME_APPLICATION_JSON:
        response_content_type = MIME_APPLICATION_JSON
        if not json_capable:
            return JSONResponse(content={"error": "JSON encoding not supported"}, status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    # Unsupported Content-Type
    else:
        return JSONResponse(content={"error": "Unsupported Media Type"}, status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    # If the Content-Type is supported, respond with 204 No Content
    return Response(status_code=HTTPStatus.NO_CONTENT, media_type=response_content_type)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, ssl_keyfile="keyfile.pem", ssl_certfile="certfile.pem")
