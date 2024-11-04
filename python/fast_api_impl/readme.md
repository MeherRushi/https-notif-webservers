
# Fast API Implemtation

- Fast API is based on ASGI based implemenation - based on uvicorn


- Here, we enable SSL using certificates  and they are generated using the following command

```bash
openssl req -x509 -newkey rsa:2048 -keyout keyfile.pem -out certfile.pem -days 365 -nodes
```

- command to run 

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --ssl-keyfile keyfile.pem --ssl-certfile certfile.pem --reload

```