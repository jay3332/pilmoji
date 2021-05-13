from .constants import EMOJI_REGEX


def get_nodes(lines):
    mappings = []
    for line in lines:
        buffer = []
        for match in EMOJI_REGEX.finditer(line):
            if specific := match.group('twemoji'):
                buffer.append({
                    'type': 'twemoji',
                    'text': specific,
                    'span': match.span()
                })
            elif specific := match.group('discord'):
                buffer.append({
                    'type': 'discord',
                    'text': specific,
                    'span': match.span()
                })
        mappings.append(buffer)

    final = []
    for line, mapping in zip(lines, mappings):
        buffer = []
        if not len(mapping):
            buffer.append({
                'content': line,
                'type': 'text'
            })
        else:
            idx = 0
            for data in mapping:
                buffer.append({
                    'content': line[idx:data['span'][0]],
                    'type': 'text'
                })
                buffer.append({
                    'content': data['text'],
                    'type': data['type']
                })
                idx = data['span'][1]

            buffer.append({
                'content': line[idx:],
                'type': 'text'
            })
        final.append(buffer)

    return final
