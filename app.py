from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp
import os
import tempfile

app = Flask(__name__)

# 首頁：載入前端網頁
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

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'title': info.get('title', '未命名影片'),
                'author': info.get('uploader', '未知頻道'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration_string', ''),
                'formats': [{
                    'id': 'best',
                    'label': '最高原畫質 (包含 4K/1080p)',
                    'resolution': 'Max',
                }]
            })
    except Exception as e:
        return jsonify({'error': '解析失敗，請確認網址是否正確。'}), 500

# API：真實下載影片
@app.route('/api/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return "請提供網址", 400
    
    # 建立一個雲端暫存資料夾
    temp_dir = tempfile.mkdtemp()
    
    # 設定下載最高畫質影像 + 最高畫質音訊，並自動合併為 mp4
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # 因為合併後副檔名必定為 .mp4，所以要替換副檔名
            base, ext = os.path.splitext(filename)
            final_filename = base + '.mp4'
            
            if not os.path.exists(final_filename):
                final_filename = filename # 備用
            
            # 將檔案傳送給使用者的瀏覽器下載
            return send_file(final_filename, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
