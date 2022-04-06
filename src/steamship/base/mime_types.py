class MimeTypes:
    UNKNOWN = "unknown"
    TXT = "text/plain"
    JSON = "application/json"
    MKD = "text/markdown"
    EPUB = "application/epub+zip"
    PDF = "application/pdf"
    JPG = "image/jpeg"
    PNG = "image/png"
    TIFF = "image/tiff"
    GIF = "image/gif"
    HTML = "text/html"
    DOC = "application/msword"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    PPT = "applicatino/ms-powerpoint"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    RTF = "application/rtf"
    BINARY = "application/octet-stream"


TEXT_MIME_TYPES = [
    MimeTypes.TXT,
    MimeTypes.MKD,
    MimeTypes.HTML,
    MimeTypes.DOCX,
    MimeTypes.PPTX
]
