import json
import os

from django.conf import settings

AUDIO_DIR = os.path.join(settings.BASE_DIR, 'audio')
AUDIO_EXTS = ('.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac')


def _list_audio_files():
    """Filenames of the audio files in the audio/ directory, sorted."""
    if not os.path.isdir(AUDIO_DIR):
        return []
    return sorted(
        name for name in os.listdir(AUDIO_DIR)
        if name.lower().endswith(AUDIO_EXTS)
        and os.path.isfile(os.path.join(AUDIO_DIR, name))
    )


def audio_files(request):
    """Make the available audio files available to every template.

    `audio_files`      -> Python list (for {% for %} option loops)
    `audio_files_json` -> JSON array literal (for inline JS)
    """
    files = _list_audio_files()
    return {'audio_files': files, 'audio_files_json': json.dumps(files)}
