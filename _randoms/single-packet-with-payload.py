def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2
                           )

    # Define your payloads here. This can be a list of strings or any other iterable.
    payloads = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]

    # Ensure the payloads list does not exceed 20 entries
    if len(payloads) > 20:
        payloads = payloads[:20]

    # Set the number of requests to the length of the payloads list
    num_requests = len(payloads)

    for i in range(num_requests):
        # Modify the request to include the payload using str.replace
        request = target.req.replace("__PAYLOAD__", payloads[i])
        engine.queue(request, gate='race1')

    engine.openGate('race1')

def handleResponse(req, interesting):
    table.add(req)
