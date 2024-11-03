# Flask Implemtation

- Flask is based on WSGI based implemenation
- So here we can use any standard webserver with the application server addition (werkzeug library)[https://stackoverflow.com/questions/37004983/what-exactly-is-werkzeug]

- synchronously handles requests but we can set the number of worker nodes

- Here, we enable SSL using self signed certificates while `    app.run(ssl_context='adhoc') ` and `--cert=adhoc` flag

- We can also generate a certificate using openssl and then use them as mentioned in the reference links (https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https)


```bash
 flask run --host=127.0.0.1 --port=8080 --cert=adhoc
```