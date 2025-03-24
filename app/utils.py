import random
from django.core.files.storage import default_storage
from django.conf import settings
import os
import string


def is_punctuation(char):
    return char in string.punctuation


def scramble_word(word):
    if len(word) <= 3:
        return word

    last_letter_idx = len(word) - 1
    while last_letter_idx > 0 and is_punctuation(word[last_letter_idx]):
        last_letter_idx -= 1

    if last_letter_idx <= 0:
        return word

    core_part = word[:last_letter_idx + 1]
    punctuation_part = word[last_letter_idx + 1:]

    if len(core_part) > 3:
        first_letter = core_part[0]
        last_letter = core_part[-1]
        middle = list(core_part[1:-1])
        random.shuffle(middle)
        core_part = first_letter + ''.join(middle) + last_letter

    return core_part + punctuation_part


def scramble_text(text):
    return ' '.join(scramble_word(word) for word in text.split())

def handle_uploaded_file(f):
    file_path = os.path.join(settings.MEDIA_ROOT, f.name)
    with default_storage.open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path
