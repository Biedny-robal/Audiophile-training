import subprocess
import tempfile
import os
from django.shortcuts import render
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings

AUDIO_DIR = os.path.join(settings.BASE_DIR, 'audio')


def menu(request):
    return render(request, 'player/menu.html')


def index(request):
    return render(request, 'player/index.html')


def loudness(request):
    return render(request, 'player/loudness.html')


def _validated_audio_path(audio_filename):
    """Return absolute path after validating filename is safe. Returns None if invalid."""
    if not audio_filename:
        return None
    if '..' in audio_filename or '/' in audio_filename or '\\' in audio_filename:
        return None
    path = os.path.join(AUDIO_DIR, audio_filename)
    if not os.path.abspath(path).startswith(os.path.abspath(AUDIO_DIR)):
        return None
    if not os.path.exists(path):
        return None
    return path


def serve_raw_audio(request):
    """
    Stream a raw (unprocessed) audio file to the browser.
    The loudness game applies gain entirely in the browser via Web Audio API,
    so no ffmpeg processing is needed here.

    Query params:
        file (str): filename within the audio directory (e.g. 'Gray_noise.wav')
    """
    audio_filename = request.GET.get('file', 'Gray_noise.wav')
    path = _validated_audio_path(audio_filename)

    if path is None:
        if not os.path.exists(os.path.join(AUDIO_DIR, audio_filename)):
            raise Http404(f"{audio_filename} not found.")
        return HttpResponse("Invalid filename", status=400, content_type='text/plain')

    return FileResponse(open(path, 'rb'), content_type='audio/wav')


def serve_audio(request):
    """
    Process audio file with ffmpeg, applying a parametric EQ band boost,
    and stream the resulting audio back to the browser.

    Query params:
        freq (int): centre frequency in Hz for the equalizer band
        file (str): name of the audio file to process
    """
    audio_filename = request.GET.get('file', 'Gray_noise.wav')
    path = _validated_audio_path(audio_filename)

    if path is None:
        if not os.path.exists(os.path.join(AUDIO_DIR, audio_filename)):
            raise Http404(f"{audio_filename} not found in audio directory.")
        return HttpResponse("Invalid filename", status=400, content_type='text/plain')

    try:
        freq = int(request.GET.get('freq', 0))
    except (ValueError, TypeError):
        freq = 0

    eq_filter = f"equalizer=f={freq}:w=10:g=12"

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        subprocess.run(
            ['ffmpeg', '-y', '-i', path, '-filter:a', eq_filter, tmp_path],
            check=True,
            capture_output=True,
        )
        with open(tmp_path, 'rb') as f:
            audio_data = f.read()
    except subprocess.CalledProcessError as e:
        return HttpResponse(
            f"ffmpeg error: {e.stderr.decode()}", status=500, content_type='text/plain'
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return HttpResponse(audio_data, content_type='audio/wav')