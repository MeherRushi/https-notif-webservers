-- This function will be called for every response received by wrk
wrk.onResponse = function(status, headers, body)
    print("Response status code: " .. status)
end

-- Send a correct POST request
wrk.method = "POST"
wrk.body = '{"ietf-https-notif:notification": {"eventTime": "2013-12-21T00:01:00Z", "event": {"event-class": "fault", "reporting-entity": {"card": "Ethernet0"}, "severity": "major"}}}'
wrk.headers["Content-Type"] = "application/json"

