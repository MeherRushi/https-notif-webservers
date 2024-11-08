const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const https = require('https');  // Import HTTPS
const yang = require('yang-js');  // Importing yang-js

const app = express();
const port = 3000;

// Middleware to parse JSON and XML bodies
app.use(bodyParser.json());
app.use(bodyParser.text({ type: 'application/xml' }));

// Define constants
const URN_ENCODING_JSON = "urn:ietf:capability:https-notf-receiver:encoding:json";
const URN_ENCODING_XML = "urn:ietf:capability:https-notf-receiver:encoding:xml";
const JSON_RECEIVER_CAPABILITIES = "receiver-capabilities";
const JSON_RECEIVER_CAPABILITY = "receiver-capability";
const UHTTPS_CONTENT_TYPE = 'Content-Type';
const UHTTPS_ACCEPT = 'Accept';

const MIME_APPLICATION_XML = "application/xml";
const MIME_APPLICATION_JSON = "application/json";

let json_capable = true;
let xml_capable = true;

// YANG Model paths
const yangDirPath = path.join(__dirname, "../../yang_modules/");  // Modify this as needed
const yangLibraryPath = path.join(__dirname, "../../yang_modules/yang-library.json");  // Modify this as needed

let yangModel = null;

// Load YANG schema from a file
fs.readFile(yangLibraryPath, 'utf8', (err, data) => {
  if (err) {
    console.error("Error loading YANG schema:", err);
    return;
  }

  // Use yang-js API to load the YANG model
  try {
    yangModel = yang.YangModel.fromJson(data);  // `fromJson` is used to load JSON schema
    console.log("YANG schema loaded successfully");
  } catch (e) {
    console.error("Error parsing YANG schema:", e);
  }
});

// Function to build capabilities data
function buildCapabilitiesData(jsonCapable, xmlCapable) {
  let capabilitiesData = [];
  if (jsonCapable) {
    capabilitiesData.push(URN_ENCODING_JSON);
  }
  if (xmlCapable) {
    capabilitiesData.push(URN_ENCODING_XML);
  }
  return capabilitiesData;
}

// Function to build XML response
function buildXML(capabilitiesData) {
  let xmlContent = '<receiver-capabilities>';
  capabilitiesData.forEach(capability => {
    xmlContent += `    <receiver-capability>${capability}</receiver-capability>\n`;
  });
  xmlContent += '</receiver-capabilities>';
  return xmlContent;
}

// Function to build JSON response
function buildJSON(capabilitiesData) {
  return JSON.stringify({
    [JSON_RECEIVER_CAPABILITIES]: {
      [JSON_RECEIVER_CAPABILITY]: capabilitiesData,
    }
  }, null, 2);
}

// Validation function (uses yang-js)
function validateRelayNotif(dataString) {
  let jsonData = null;
  try {
    jsonData = JSON.parse(dataString);
  } catch (e) {
    // If JSON parsing fails, try parsing as XML
    try {
      const xmlData = dataString;
      // Convert XML to JSON
      const parsedXML = new DOMParser().parseFromString(xmlData, 'text/xml');
      // Convert parsedXML into JSON (this may require custom handling based on your XML structure)
      jsonData = { "ietf-https-notif:notification": parsedXML };  // Simplified for example
    } catch (err) {
      return false;  // Return false if both JSON and XML parsing fails
    }
  }

  // Validate the parsed data using yang-js
  try {
    // Assuming the method is `yangModel.validate()` or similar in yang-js
    const isValid = yangModel.validate(jsonData);  // This is an example method; adjust according to the actual method
    return isValid;
  } catch (err) {
    return false;
  }
}

// Route for capabilities
app.get('/capabilities', (req, res) => {
  const capabilitiesData = buildCapabilitiesData(json_capable, xml_capable);

  const acceptHeader = req.get(UHTTPS_ACCEPT);
  if (acceptHeader) {
    const qXml = getQValue(acceptHeader, MIME_APPLICATION_XML);
    const qJson = getQValue(acceptHeader, MIME_APPLICATION_JSON);
    
    if (qXml > qJson && xml_capable) {
      res.set('Content-Type', MIME_APPLICATION_XML).send(buildXML(capabilitiesData));
    } else {
      res.set('Content-Type', MIME_APPLICATION_JSON).send(buildJSON(capabilitiesData));
    }
  } else {
    res.set('Content-Type', MIME_APPLICATION_JSON).send(buildJSON(capabilitiesData));
  }
});

// Route for relay notification
app.post('/relay-notification', (req, res) => {
  const reqContentType = req.get(UHTTPS_CONTENT_TYPE);

  if (!reqContentType) {
    return res.status(415).send("Content-type is None -> Empty Body Notification");
  }

  if (reqContentType === MIME_APPLICATION_XML && !xml_capable) {
    return res.status(415).send("XML encoding not supported");
  }

  if (reqContentType === MIME_APPLICATION_JSON && !json_capable) {
    return res.status(415).send("JSON encoding not supported");
  }

  if (validateRelayNotif(req.body)) {
    return res.status(204).send();  // No Content
  } else {
    return res.status(400).send("Relay notification doesn't correspond with the YANG model");
  }
});

// Function to extract q-value from Accept header
function getQValue(acceptHeader, mediaType) {
  const regex = new RegExp(`${mediaType}(;q=([0-9.]+))?`);
  const match = acceptHeader.match(regex);
  if (match) {
    return match[2] ? parseFloat(match[2]) : 1.0;
  }
  return 0.0;
}

// SSL/TLS certificates for HTTPS
const sslOptions = {
  key: fs.readFileSync(path.join(__dirname, '../../certs/server.key')),
  cert: fs.readFileSync(path.join(__dirname, '../../certs/server.crt')),
};

// Create HTTPS server
https.createServer(sslOptions, app).listen(port, () => {
  console.log(`HTTPS server is running on https://localhost:${port}`);
});
