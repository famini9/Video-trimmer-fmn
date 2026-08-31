from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import ffmpeg
import os
import uuid
from datetime import datetime

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_info', methods=['POST'])
def get_info():
    url = request.json['url']
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return jsonify({
        'title': info['title'],
        'duration': info['duration'],
        'thumbnail': info['thumbnail']
    })

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data['url']
    start = int(data['start'])
    end = int(data['end'])
    format = data['format']
    
    unique_id = str(uuid.uuid4())
    temp_file = os.path.join(DOWNLOAD_FOLDER, f'{unique_id}.temp')
    output_file = os.path.join(DOWNLOAD_FOLDER, f'{unique_id}.{format}')
    
    ydl_opts = {'format': 'bestvideo[height<=1080]+bestaudio/best', 'outtmpl': temp_file}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    duration = end - start
    if format == 'mp3':
        ffmpeg.input(temp_file, ss=start, t=duration).output(output_file, audio_bitrate='192k').run(overwrite_output=True)
    else:
        ffmpeg.input(temp_file, ss=start, t=duration).output(output_file, vcodec='libx264', acodec='aac').run(overwrite_output=True)
    
    os.remove(temp_file)
    return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
