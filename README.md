# Audiophile-training
Python GUI application for training a Users ability to listen intently and distinguish different sound parameters.

## Audio Files
Place your audio files in the `audio/` directory. The application supports WAV files. Currently included:
- `Gray_noise.wav` - Gray noise sample
- `sample.wav` - 440Hz sine wave sample

## Installing & running:
FFMPEG is required, if you don't have ffmpeg installed;
```
sudo apt install ffmpeg -y
```
Creating a virtual python environment is recommended. Once the venv is created and you've entered it run
```
pip install -r requirements.txt
```
Then startup the app with
```
python manage.py runserver
```
the app should now be available on [http://127.0.0.1:8000](http://127.0.0.1:8000)
