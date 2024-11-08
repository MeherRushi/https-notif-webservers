# Flask Implemtation

- Flask is based on WSGI based implemenation
- So here we can use any standard webserver with the application server addition (werkzeug library)[https://stackoverflow.com/questions/37004983/what-exactly-is-werkzeug]

- synchronously handles requests but we can set the number of worker nodes

- Here, we enable SSL using self signed certificates while `    app.run(ssl_context='adhoc') ` and `--cert=adhoc` flag

- We can also generate a certificate using openssl and then use them as mentioned in the reference links (https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https)


- dev
```bash
flask run --host=127.0.0.1 --port=8080 --cert=../../certs/server.crt --key=../../certs/server.key
```

- prod
```bash
gunicorn -w 5 --certfile ../../certs/server.crt --keyfile ../../certs/server.key -b 127.0.0.1:4433 app:app
```

- generating the library yang file for yangson

```bash
python3 mkylib.py ../../../https-notif-servers/yang_modules/
```
```
{
  "ietf-yang-library:modules-state": {
    "module-set-id": "",
    "module": [
      {
        "name": "ietf-https-notif",
        "revision": "",
        "namespace": "urn:ietf:params:xml:ns:netconf:notification:1.0",
        "conformance-type": "implement"
      },
      {
        "name": "ietf-yang-types",
        "revision": "2013-07-15",
        "namespace": "urn:ietf:params:xml:ns:yang:ietf-yang-types",
        "conformance-type": "import"
      }
    ]
  }
}
```

Eg for valid json data

```
{
    "ietf-https-notif:notification": {
    "eventTime": "2013-12-21T00:01:00Z",
    "event" : {
        "event-class" : "fault",
        "reporting-entity" : { "card" : "Ethernet0" },
        "severity" : "major"
    }
    }
}
```

Eg for valid xml data

```
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
  <eventTime>2013-12-21T00:01:00Z</eventTime>
  <event>
    <event-class>fault</event-class>
    <reporting-entity>
      <card>Ethernet0</card>
    </reporting-entity>
    <severity>major</severity>
  </event>
</notification>
```


