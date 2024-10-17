from __future__ import unicode_literals
from flask import Flask, request, send_file, render_template, redirect, flash, send_from_directory
from pytubefix import YouTube  # Import YouTube from pytubefix
from pytubefix.cli import on_progress  # Import on_progress callback from pytubefix
import os
import yt_dlp

app = Flask(__name__)
app.secret_key = "neo"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/terms-conditions')
def terms():
    return render_template('terms-conditions.html')


@app.route('/download', methods=["POST", "GET"])
def download_mp3():
    url = request.form.get("url", None)
    if not url:
        flash('Please enter a valid URL.')
        return render_template('index.html')
    try:
        # Try with pytubefix first
        yt = YouTube(url, on_progress_callback=on_progress)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download()
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        return send_file(new_file, as_attachment=True)

    except Exception as e:
        # If pytube (pytubefix) fails, use yt-dlp
        print("Pytubefix encountered an error, falling back to yt-dlp: ", str(e))
        try:
            ydl_opts = {
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info_dict)
                filename = filename.rsplit(".", 1)[0] + ".mp3"
                return send_from_directory('downloads', os.path.basename(filename), as_attachment=True)
        except Exception as e:
            flash(str(e))
            return render_template('index.html')





# download video under maintenance for now.
@app.route('/downloadvid', methods=["POST", "GET"])
def download_video():
    try:
        url = request.form.get("url", None)
        if not url:
            flash('Please enter a valid URL.')
            return render_template('index.html')

        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'bestvideo[ext=mp4][vcodec=avc1]+bestaudio[ext=m4a]/mp4+best[height<=480]'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            return send_from_directory('downloads', os.path.basename(filename), as_attachment=True)
    except Exception as e:
        flash(str(e))
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

    #app.run(port=5000, debug=True)

