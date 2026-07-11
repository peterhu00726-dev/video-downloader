FROM python:3.10-slim

# 安裝高畫質合併必需的 ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 啟動伺服器
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app", "--timeout", "300"]