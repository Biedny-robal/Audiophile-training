import subprocess
import tempfile
import os
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings

# Path to the audio files directory
AUDIO_DIR = os.path.join(settings.BASE_DIR, 'audio')


def index(request):
    """Render the main player page."""
    return render(request, 'player/index.html')


def serve_audio(request):
    """
    Process audio file with ffmpeg, applying a bass EQ boost/cut,
    and stream the resulting audio back to the browser.

    Query params:
        bass (int): gain in dB for the low-frequency equalizer band.
                    Positive = louder bass, negative = quieter.
                    Clamped to [0, 20] on the server for safety.
        file (str): name of the audio file to process (e.g., 'Gray_noise.wav', 'sample.wav')
    """
    # Get the requested audio file
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

    # Read and clamp the requested bass gain
    try:
        bass_gain = int(request.GET.get('bass', 0))
    except (ValueError, TypeError):
        bass_gain = 0
    bass_gain = max(0, min(20, bass_gain))

    # Build the ffmpeg filter:
    #   equalizer=f=100        — centre frequency 100 Hz (upper bass)
    #   width_type=o           — width measured in octaves
    #   width=2                — 2-octave band (covers ~50–200 Hz)
    #   g=<gain>               — gain in dB
    # When gain is 0 we still run through ffmpeg so the pipeline is uniform,
    # but you could short-circuit and serve the raw file if you prefer.
    eq_filter = f"volume={bass_gain/10}"

    # Write ffmpeg output into a temporary file so we can stream it cleanly.
    # We use a named temp file because ffmpeg needs a seekable output target
    # for WAV headers; streaming to a pipe would require -f wav explicitly.
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
