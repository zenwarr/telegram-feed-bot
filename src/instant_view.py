import urllib.parse


def get_instant_view_link(instant_view_rhash, source_url):
    return f"https://t.me/iv?url={urllib.parse.quote_plus(source_url)}&rhash={instant_view_rhash}"
