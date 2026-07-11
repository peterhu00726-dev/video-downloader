# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp
import os
import tempfile

app = Flask(__name__)

# 載入前端網頁
@app.route('/')
def index():
    return render_template('index.html')

# API：解析影片資訊
@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': '請提供網址'}), 400

    # 設定安全偽裝標頭，防止雲端伺服器連線被拒絕
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'nocheckcertificate': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 動態返回下載選項
            return jsonify({
                'title': info.get('title', '未命名影片'),
                'author': info.get('uploader', '未知頻道'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration_string', ''),
                'formats': [
                    {'id': 'best', 'label': '⭐ 原始最高原畫質 (支援 4K/1080p)'},
                    {'id': '1080', 'label': '⚡ Full HD 畫質 (1080p)'},
                    {'id': '720', 'label': '🎬 HD 標準畫質 (720p)'},
                ]
            })
    except Exception as e:
        print(f"解析失敗: {str(e)}")
        return jsonify({'error': '影片解析失敗。請確認影片網址是否正確。'}), 500

# API：真實影片下載路由
@app.route('/api/download', methods=['GET'])
def download():
    url = request.args.get('url')
    quality = request.args.get('quality', 'best')
    if not url:
        return "請提供網址", 400
    
    temp_dir = tempfile.mkdtemp()
    
    # 依選擇的畫質調配影音合併指令
    format_str = 'bestvideo+bestaudio/best'
    if quality == '1080':
        format_str = 'bestvideo[height<=1080]+bestaudio/best'
    elif quality == '720':
        format_str = 'bestvideo[height<=720]+bestaudio/best'

    ydl_opts = {
        'format': format_str,
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # 合併後的最終檔案必然為 mp4，因此需校正副檔名
            base, ext = os.path.splitext(filename)
            final_filename = base + '.mp4'
            
            if not os.path.exists(final_filename):
                final_filename = filename
            
            # 將合併完成的 mp4 檔案真實傳回至使用者的瀏覽器中
            return send_file(final_filename, as_attachment=True)
    except Exception as e:
        print(f"下載失敗: {str(e)}")
        return "下載失敗，請稍後重試。", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
