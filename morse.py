#!/usr/bin/env python
# -*- coding: utf-8 -*-


MORSE_ALPHABET = {
    'A': '.-',
    'B': '-...',
    'C': '-.-.',
    'D': '-..',
    'E': '.',
    'F': '..-.',
    'G': '--.',
    'H': '....',
    'I': '..',
    'J': '.---',
    'K': '-.-',
    'L': '.-..',
    'M': '--',
    'N': '-.',
    'O': '---',
    'P': '.--.',
    'Q': '--.-',
    'R': '.-.',
    'S': '...',
    'T': '-',
    'U': '..-',
    'V': '...-',
    'W': '.--',
    'X': '-..-',
    'Y': '-.--',
    'Z': '--..',
    '1': '.----',
    '2': '..---',
    '3': '...--',
    '4': '....-',
    '5': '.....',
    '6': '-....',
    '7': '--...',
    '8': '---..',
    '9': '----.',
    '0': '-----',
    '.': '.-.-.-',
    ',': '--..--',
    ':': '---...',
    '?': '..--..',
    '\'': '.----.',
    '-': '-....-',
    '/': '-..-.',
    '@': '.--.-.',
    '=': '-...-',
    ' ': '/'
}

INVERSE_MORSE_ALPHABET = dict([(v, k) for k, v in MORSE_ALPHABET.items()])


def decode_morse(code, position=0):
    if position < len(code) - 1:
        morse_latter = ''
        for key, char in enumerate(code[position:]):
            if char == ' ':
                position += key + 1
                latter = INVERSE_MORSE_ALPHABET.get(morse_latter, '***')
                return latter + decode_morse(code, position=position)
            else:
                morse_latter += char
    else:
        return ''


def encode_morse(message):
    morse_latter = ''
    for char in message[:]:
        morse_latter += MORSE_ALPHABET.get(char.upper(), ' ') + ' '
    return morse_latter


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=u'莫尔斯码转义')
    parser.add_argument('-c', '--code',
                        dest='code',
                        help=u'莫尔斯码')
    parser.add_argument('-m', '--message',
                        dest='message',
                        help=u'英文文本')
    options = parser.parse_args()

    if options.code:
        print decode_morse(options.code)

    if options.message:
        print encode_morse(options.message)
