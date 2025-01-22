def queueRequests(target, wordlists):

    # Initialize the RequestEngine with HTTP/2 support
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2
                           )

    # Specify the path to the wordlist file
    wordlist_path = '/Users/prasanth/wordlist/num.txt'
    
    # Load the wordlist from the specified path
    with open(wordlist_path, 'r') as f:
        wordlist = f.read().splitlines()

    # Limit to the first 20 lines of the wordlist
    limited_wordlist = wordlist[:20]

    # Queue requests using words from the limited wordlist
    for word in limited_wordlist:
        # Modify the request using the word (placing it in the position where %s is specified)
        modified_request = target.req % word
        engine.queue(modified_request, gate='race1')

    # Send all queued requests in sync
    engine.openGate('race1')


def handleResponse(req, interesting):
    if interesting:
        table.add(req)