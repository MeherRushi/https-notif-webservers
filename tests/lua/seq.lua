-- Send a correct GET
if wrk.counter == 1 then
    wrk.method = "GET"
    return wrk.format(nil)
end

-- Send a correct JSON POST
if wrk.counter == 2 then
    wrk.method = "POST"
    wrk.body = '{"ietf-https-notif:notification": {"eventTime": "2013-12-21T00:01:00Z", "event": {"event-class": "fault", "reporting-entity": {"card": "Ethernet0"}, "severity": "major"}}}'
    wrk.headers["Content-Type"] = "application/json"
    return wrk.format(nil)
end

-- Send a malformed JSON POST (missing closing brackets)
if wrk.counter == 3 then
    wrk.method = "POST"
    wrk.body = '{"ietf-https-notif:notification": {"eventTime": "2013-12-21T00:01:00Z", "event": {"event-class": "fault"}}'  -- Missing closing brackets
    wrk.headers["Content-Type"] = "application/json"
    return wrk.format(nil)
end

-- Send a correct XML POST
if wrk.counter == 4 then
    wrk.method = "POST"
    wrk.body = [[
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
]]
    wrk.headers["Content-Type"] = "application/xml"
    return wrk.format(nil)
end

-- Send a malformed XML POST (missing closing tag)
if wrk.counter == 5 then
    wrk.method = "POST"
    wrk.body = [[
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
  <eventTime>2013-12-21T00:01:00Z</eventTime>
  <event>
    <event-class>fault</event-class>
    <reporting-entity>
      <card>Ethernet0</card>
    </reporting-entity>
]]  -- Missing closing </event> and </notification> tags
    wrk.headers["Content-Type"] = "application/xml"
    return wrk.format(nil)
end

-- Send a 404 request
if wrk.counter == 6 then
    wrk.method = "GET"
    wrk.body = nil
    wrk.headers["Content-Type"] = nil
    return wrk.format("GET /nonexistent-endpoint HTTP/1.1\r\n")
end

-- Repeat the process
return nil

