from fastapi import FastAPI, Request, Response, Header, HTTPException, status
from typing import Optional
import json
import xml.etree.ElementTree as ET
import subprocess
import re

# Define constants
NAMESPACE = "urn:ietf:params:xml:ns:yang:example"
URN_ENCODING_JSON = "urn:ietf:capability:https-notif-receiver:encoding:json"
URN_ENCODING_XML = "urn:ietf:capability:https-notif-receiver:encoding:xml"
MIME_APPLICATION_XML = "application/xml"
MIME_APPLICATION_JSON = "application/json"

# Define file paths
data_file_path = "../../get_yang_files_and_validators/example-config.xml"  # Make this configurable
yang_model_path = "../../get_yang_files_and_validators/example.yang"         # Make this configurable

app = FastAPI()


def read_data_set_server_capabilities(file_path):
    if file_path.endswith(".xml"):
        return parse_xml_capabilities(file_path)
    elif file_path.endswith(".json"):
        return parse_json_capabilities(file_path)
    return False, False, []


def parse_xml_capabilities(file_path):
    capabilities_data = []
    tree = ET.parse(file_path)
    root = tree.getroot()

    for capability in root.findall(f"{{{NAMESPACE}}}receiver-capabilities"):
        receiver_capability = capability.find(f"{{{NAMESPACE}}}receiver-capability")
        if receiver_capability is not None:
            capabilities_data.append(receiver_capability.text)

    json_capable = URN_ENCODING_JSON in capabilities_data
    xml_capable = URN_ENCODING_XML in capabilities_data
    return json_capable, xml_capable, capabilities_data


def parse_json_capabilities(file_path):
    capabilities_data = []
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
        receiver_capabilities = data.get("receiver-capabilities", {})
        capabilities = receiver_capabilities.get("receiver-capability", [])
        capabilities_data.extend(capabilities)

    json_capable = URN_ENCODING_JSON in capabilities_data
    xml_capable = URN_ENCODING_XML in capabilities_data
    return json_capable, xml_capable, capabilities_data


def build_xml(capabilities_data):
    xml_content = f'<capabilities xmlns="{NAMESPACE}">\n'
    for capability in capabilities_data:
        xml_content += f'  <receiver-capabilities>\n'
        xml_content += f'    <receiver-capability>{capability}</receiver-capability>\n'
        xml_content += f'  </receiver-capabilities>\n'
    xml_content += '</capabilities>'
    return xml_content


def build_json(capabilities_data):
    return json.dumps({
        "receiver-capabilities": {
            "receiver-capability": capabilities_data
        }
    }, indent=2)


def call_c_program(data_file_path, yang_model_path):
    result = subprocess.run(
        ["../../get_yang_files_and_validators/yang_validate", data_file_path, yang_model_path],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def get_q_value(accept_header, media_type):
    pattern = re.compile(rf"{media_type}(;q=([0-9.]+))?")
    match = pattern.search(accept_header)
    if match:
        q_value = match.group(2)
        return float(q_value) if q_value else 1.0
    return 0.0


@app.get("/capabilities")
async def get_capabilities(accept: Optional[str] = Header(None)):
    if not call_c_program(data_file_path, yang_model_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error, incorrect data in the datastore"
        )

    json_capable, xml_capable, capabilities_data = await read_data_set_server_capabilities(data_file_path)

    q_xml = get_q_value(accept, MIME_APPLICATION_XML)
    q_json = get_q_value(accept, MIME_APPLICATION_JSON)


    """ If the desired header field is not present, the server can choose the format it prefers
    reference link : https://stackoverflow.com/questions/51006471/accept-header-in-http-request """

    if q_json == 0 and q_xml == 0:
        if xml_capable:
            return Response(content=build_xml(capabilities_data), media_type=MIME_APPLICATION_XML)
        elif json_capable:
            return Response(content=build_json(capabilities_data), media_type=MIME_APPLICATION_JSON)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No valid capabilities found"
        )

    if xml_capable and (q_xml >= q_json or not json_capable):
        return Response(content=build_xml(capabilities_data), media_type=MIME_APPLICATION_XML)

    if json_capable and q_json > 0:
        return Response(content=build_json(capabilities_data), media_type=MIME_APPLICATION_JSON)

    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="Not acceptable"
    )


@app.post("/relay-notification")
async def post_notification(content_type: Optional[str] = Header(None)):
    json_capable, xml_capable, _ = read_data_set_server_capabilities(data_file_path)

    if content_type == MIME_APPLICATION_XML:
        if not xml_capable:
            return Response(
                content=json.dumps({"error": "XML encoding not supported"}),
                media_type=MIME_APPLICATION_XML,
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT, media_type=MIME_APPLICATION_XML)

    elif content_type == MIME_APPLICATION_JSON:
        if not json_capable:
            return Response(
                content=json.dumps({"error": "JSON encoding not supported"}),
                media_type=MIME_APPLICATION_JSON,
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT, media_type=MIME_APPLICATION_JSON)

    return Response(
        content=json.dumps({"error": "Unsupported Media Type"}),
        media_type=content_type,
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    )
