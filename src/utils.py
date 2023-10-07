def utf16_codeunits_in_text(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def utf16_codeunit_index_to_pos(text: str, codeunit_index: int) -> int | None:
    encoded = text.encode("utf-16-le")

    word_offset = 0
    char_index = 0
    while word_offset < len(encoded):
        if word_offset == codeunit_index:
            return char_index

        word_offset += get_utf16_char_length_at_pos(encoded, word_offset)
        char_index += 1

        if word_offset > codeunit_index:
            # position is invalid, between char boundaries
            return None

    return None


def get_utf16_char_length_at_pos(data: bytes, word_offset: int) -> int:
    word = data[word_offset * 2]
    # if word is a high surrogate
    if 0xD8 <= word <= 0xDB:
        return 2
    else:
        return 1
