-- sequence.lua
local headers = {
    ["Accept"] = "application/json"
}

request = function()
    local q_value_json = math.random()  -- Random q value between 0 and 1
    local q_value_xml = math.random()   -- Random q value between 0 and 1

    -- Randomly decide the combination of Accept header
    local accept_header = ""

    -- Randomly choose between:
    -- 1. application/json or application/xml with q value
    -- 2. both application/json and application/xml without q value
    -- 3. Only one of application/json or application/xml

    local choice = math.random(1, 3)
    
    if choice == 1 then
        -- Include both JSON and XML with q values
        accept_header = "application/json;q=" .. string.format("%.1f", q_value_json) .. ", application/xml;q=" .. string.format("%.1f", q_value_xml)
    elseif choice == 2 then
        -- Include both JSON and XML without q values
        accept_header = "application/json, application/xml"
    else
        -- Randomly choose between JSON or XML alone
        if math.random() > 0.5 then
            accept_header = "application/json;q=" .. string.format("%.1f", q_value_json)
        else
            accept_header = "application/xml;q=" .. string.format("%.1f", q_value_xml)
        end
    end

    -- Set the Accept header for the request
    headers["Accept"] = accept_header
    
    -- Send the GET request to the /capabilities endpoint with the dynamic headers
    return wrk.format("GET", "/capabilities", headers)
end

