import subprocess
import tempfile
import os
from django.shortcuts import render
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from django.views.decorators.http import require_GET

AUDIO_DIR = os.path.join(settings.BASE_DIR, 'audio')


def menu(request):
    return render(request, 'player/menu.html')

def eq_trainer(request):
    """Render the EQ trainer game page."""
    return render(request, 'player/eq_trainer.html')

def index(request):
    return render(request, 'player/index.html')

def loudness_ab(request):
    """Render the EQ trainer game page."""
    return render(request, 'player/loudness_ab.html')

def spatial(request):
    """Render the Spatial trainer game page."""
    return render(request, 'player/spatial.html')

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

@require_GET
def serve_bandwidth_audio(request):
    if not request.GET.get('file'):
        return render(request, 'player/bandwidth.html')
    audio_filename = request.GET.get('file', 'Gray_noise.wav')

    if '..' in audio_filename or '/' in audio_filename or '\\' in audio_filename:
        return HttpResponse("Invalid filename", status=400, content_type='text/plain')
    AUDIO_FILE = os.path.join(AUDIO_DIR, audio_filename)
    
    if audio_filename.endswith('.wav'):
        content_type = 'audio/wav'
    else:
        content_type = 'audio/mpeg'
    # Ensure the file is within the audio directory
    if not os.path.abspath(AUDIO_FILE).startswith(os.path.abspath(AUDIO_DIR)):
        return HttpResponse("Invalid filename", status=400, content_type='text/plain')
    
    if not os.path.exists(AUDIO_FILE):
        raise Http404(f"{audio_filename} not found in audio directory.")
    # Band cutoff is done in frontend
    return HttpResponse(open(AUDIO_FILE, 'rb').read(), content_type=content_type)

@require_GET
def loudness_audio(request):

    audio_filename = request.GET.get('file', 'Gray_noise.wav')
    
    # Validate filename to prevent directory traversal
    if '..' in audio_filename or '/' in audio_filename or '\\' in audio_filename:
        return HttpResponse("Invalid filename", status=400, content_type='text/plain')
    
    AUDIO_FILE = os.path.join(AUDIO_DIR, audio_filename)
    
    # Ensure the file is within the audio directory
    if not os.path.abspath(AUDIO_FILE).startswith(os.path.abspath(AUDIO_DIR)):
        return HttpResponse("Invalid filename", status=400, content_type='text/plain')
    
    if not os.path.exists(AUDIO_FILE):
        raise Http404(f"{audio_filename} not found in audio directory.")
    
    mode = request.GET.get("mode","boost")
    version = request.GET.get("version", "A")
    louder  = request.GET.get("louder", "A")
    gain    = float(request.GET.get("gain", 2))
    if mode == "boost":
        if version == louder:
            eq_filter = f"volume={gain}dB"
        else:
            eq_filter = "volume=0dB"
    else:
        if version == louder:
            eq_filter = "volume=0dB"
        else:
            eq_filter = f"volume=-{gain}dB"
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        subprocess.run(
            [
                'ffmpeg',
                '-y',                   # overwrite output without asking
                '-i', AUDIO_FILE,       # input file
                '-filter:a', eq_filter,       # audio filter (bass EQ)
                tmp_path,               # output file
            ],
            check=True,
            capture_output=True,        # suppress ffmpeg's verbose console output
        )
        with open(tmp_path, 'rb') as f:
            audio_data = f.read()

    except subprocess.CalledProcessError as e:
        return HttpResponse(
            f"ffmpeg error: {e.stderr.decode()}", status=500, content_type='text/plain'
        )
    finally:
        # Always clean up the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return HttpResponse(audio_data, content_type='audio/wav')