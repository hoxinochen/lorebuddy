from lorebuddy.acquisition.media_types import detect_encoding, detect_media_type


def test_signature_overrides_extension_with_conflict():
    result = detect_media_type("wrong.txt", b"\x89PNG\r\n\x1a\nrest")
    assert result.detected_media_type == "image/png"
    assert result.confidence == "conflict"


def test_html_charset_is_evidence_not_transcoding():
    raw = b'<meta charset="gbk"><p>test</p>'
    media = detect_media_type("x.htm", raw)
    encoding = detect_encoding(raw, media.detected_media_type)
    assert encoding.declared_encoding == "gbk"
    assert encoding.detected_encoding_candidate == "utf-8"
    assert encoding.conflict


def test_binary_encoding_is_not_applicable():
    result = detect_encoding(b"\x00\x01", "application/octet-stream")
    assert result.confidence == "not-applicable"
    assert result.detected_encoding_candidate is None
