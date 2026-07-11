FROM python:3.10-slim

# 更新系統並安裝高畫質影音合併所必須的 ffmpeg 程式
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 啟動並執行雲端後台伺服器
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app", "--timeout", "300"]