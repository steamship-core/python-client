from steamship.utils.text_chunker import chunk_text


def test_text_chunker():
    chunked = list(chunk_text("Hi there"))
    assert len(chunked) == 1

    chunked = list(chunk_text("12345", chunk_size=1, chunk_overlap=0))
    assert len(chunked) == 5
    assert chunked == ["1", "2", "3", "4", "5"]

    chunked = list(chunk_text("12345", chunk_size=2, chunk_overlap=1))
    assert len(chunked) == 5
    assert chunked == ["12", "23", "34", "45", "5"]

    chunked = list(chunk_text("12345", chunk_size=3, chunk_overlap=2))
    assert len(chunked) == 5
    assert chunked == ["123", "234", "345", "45", "5"]
