// Graphql operationName
String q = requestResponse.request().parameterValue("query", HttpParameterType.JSON);
if (q != null) {
   return q.split("\\{|\\(")[0];
}
return "";
//or
return requestResponse.request().parameterValue("operationName", HttpParameterType.JSON);

// SOAPAction
String q = requestResponse.request().headerValue("SOAPAction");
if (q != null && !q.isEmpty()) {
    // Remove the "http://tempuri.org/" prefix from the SOAPAction value
    return q.replace("http://tempuri.org/", "").trim();
}

// If the SOAPAction header is missing or empty, fallback to parsing the body
q = requestResponse.request().bodyToString();
if (q != null) {
    // Find the start of the <soapenv:Body> or <soap:Body> tag
    int bodyStart = q.indexOf("<soapenv:Body>");
    if (bodyStart == -1) { // If <soapenv:Body> is not found, look for <soap:Body>
        bodyStart = q.indexOf("<soap:Body>");
    }
    
    if (bodyStart != -1) {
        // Find the first tag inside the <soapenv:Body> or <soap:Body>
        int tagStart = q.indexOf("<", bodyStart + 12); // Skip "<soapenv:Body>" or "<soap:Body>"
        int tagEnd = q.indexOf(" ", tagStart); // Find the first space (attributes start)
        if (tagEnd == -1 || tagEnd > q.indexOf(">", tagStart)) {
            // Adjust to the closing ">" if no attributes are present
            tagEnd = q.indexOf(">", tagStart);
        }
        if (tagStart != -1 && tagEnd != -1) {
            // Extract the tag name, skipping "<"
            return q.substring(tagStart + 1, tagEnd).trim();
        }
    }
}

// Return an empty string if both checks fail
return "";
