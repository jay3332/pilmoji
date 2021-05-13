import re
from emoji.unicode_codes import EMOJI_UNICODE


ALL_EMOJIS = list(EMOJI_UNICODE['en'].values())

_TWEMOJI_EMOJI_REGEX = '|'.join(map(re.escape, ALL_EMOJIS))
EMOJI_REGEX = re.compile(f"(?P<twemoji>{_TWEMOJI_EMOJI_REGEX})|"+r'<a?:[a-zA-Z0-9_]{2,32}:(?P<discord>[0-9]{17,})>')
