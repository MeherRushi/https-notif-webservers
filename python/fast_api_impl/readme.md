
# Flask Implemtation

- Flask is based on ASGI based implemenation - based on uvicorn


- Here, we enable SSL using  certificates while `app.run(ssl_context='adhoc') ` and they are generated using the following command

```bash
openssl req -x509 -newkey rsa:2048 -keyout keyfile.pem -out certfile.pem -days 365 -nodes
```

- command to run 

```bash
 flask run --host=127.0.0.1 --port=8080 --cert=adhoc
```