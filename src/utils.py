def utf16_code_units_in_text(text):
    return len(text.encode('utf-16-le')) // 2
