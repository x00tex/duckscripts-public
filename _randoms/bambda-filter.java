// Define a set of MIME types to exclude
var excludedMimeTypes = new HashSet<>(Arrays.asList(
    MimeType.CSS,
    MimeType.IMAGE_UNKNOWN,
    MimeType.IMAGE_JPEG,
    MimeType.IMAGE_GIF,
    MimeType.IMAGE_PNG,
    MimeType.IMAGE_BMP,
    MimeType.IMAGE_TIFF,
    MimeType.APPLICATION_FLASH,
    MimeType.LEGACY_SER_AMF
));

// Define a set of file extensions to exclude (Extended List)
var excludedExtensions = new HashSet<>(Arrays.asList(
    ".gif",".jpg",".jpeg",".png",".css",".woff",".woff2",".ttf",".svg",".ico",".webp",".mp4",
    ".avi",".mkv",".mov",".mp3",".wav",".flac",".zip",".rar",".7z",".tar",".gz",".pdf"
));

// Define a set of hostnames to include (do not filter images or binary files from these hosts)
var includedHosts = new HashSet<>(Arrays.asList(
    ""
));

// Define a set of custom URL patterns to exclude
var excludedUrlPatterns = Arrays.asList(
    ""
);

// Get the HTTP method of the request
var httpMethod = requestResponse.request().method().toUpperCase();

// Exclude requests with the HTTP method "OPTIONS"
if ("OPTIONS".equals(httpMethod)) {
    return false;
}

// Get the MIME type of the response
var mimeType = requestResponse.mimeType();

// Get the full URL of the request
var fullUrl = requestResponse.request().url();

// Extract the host from the URL without using java.net.URL
String host;
try {
    var urlParts = fullUrl.split("/");
    host = urlParts.length > 2 ? urlParts[2].toLowerCase() : "";
} catch (Exception e) {
    // If URL parsing fails, exclude the request
    return false;
}

// Get the path of the request, converted to lowercase for case-insensitive comparison
var path = requestResponse.request().pathWithoutQuery().toLowerCase();

// *** In-Scope Check ***
if (!requestResponse.request().isInScope()) {
    return false;
}

// Check if the host is in the inclusion list, if the list is not empty
if (!includedHosts.isEmpty() && includedHosts.contains(host)) {
    // If the host is in the inclusion list, include the request regardless of MIME type or extension
    return true;
}

// Check if the MIME type is excluded
if (excludedMimeTypes.contains(mimeType)) {
    return false;
}

// Check if the path ends with an excluded extension
for (var ext : excludedExtensions) {
    if (path.endsWith(ext)) {
        return false;
    }
}

// Check for custom patterns in the URL, if the list is not empty
if (!excludedUrlPatterns.isEmpty()) {
    for (var pattern : excludedUrlPatterns) {
        if (fullUrl.contains(pattern)) {
            return false;
        }
    }
}

// If none of the conditions matched, include the request
return true;
