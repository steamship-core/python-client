from enum import Enum

STEAMSHIP_PREFIX = "application/vnd.steamship-block"


class MimeTypes(str, Enum):
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
    STEAMSHIP_BLOCK_JSON = f"{STEAMSHIP_PREFIX}.json.v1"
    WAV = "audio/wav"
    MP3 = "audio/mp3"
    OGG_AUDIO = "audio/ogg"
    OGG_VIDEO = "video/ogg"
    MP4_VIDEO = "video/mp4"
    MP4_AUDIO = "audio/mp4"
    WEBM_VIDEO = "video/webm"
    WEBM_AUDIO = "audio/webm"
    FILE_JSON = "fileJson"

    # This block contains information that isn't part of the payload to/from a plugin, but instead is json-formatted
    # information about if/how the plugin supports certain behaviors.
    STEAMSHIP_PLUGIN_CAPABILITIES_REQUEST = f"{STEAMSHIP_PREFIX}.plugin-capabilities-request+json"
    STEAMSHIP_PLUGIN_CAPABILITIES_RESPONSE = f"{STEAMSHIP_PREFIX}.plugin-capabilities-response+json"
    STEAMSHIP_PLUGIN_FUNCTION_CALL_INVOCATION = (
        f"{STEAMSHIP_PREFIX}.function-calling-support-invocation+json"
    )
    STEAMSHIP_PLUGIN_FUNCTION_CALL_RESULT = (
        f"{STEAMSHIP_PREFIX}.function-calling-support-result+json"
    )

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def is_binary(cls, value):
        """Returns whether the mime type is likely a binary file."""
        return value in [
            cls.UNKNOWN,
            cls.PDF,
            cls.JPG,
            cls.PNG,
            cls.TIFF,
            cls.GIF,
            cls.DOC,
            cls.PPT,
            cls.BINARY,
            cls.WAV,
            cls.MP3,
            cls.OGG_VIDEO,
            cls.OGG_AUDIO,
            cls.MP4_AUDIO,
            cls.MP4_VIDEO,
            cls.WEBM_AUDIO,
            cls.WEBM_VIDEO,
        ]


class ContentEncodings:
    BASE64 = "base64"


TEXT_MIME_TYPES = [
    MimeTypes.TXT,
    MimeTypes.MKD,
    MimeTypes.HTML,
    MimeTypes.DOCX,
    MimeTypes.PPTX,
]
