# Sử dụng Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements trước để tận dụng Docker cache
COPY requirements.txt .

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY discord_gemini_bot.py .

# Set environment variables
ENV PORT=8000

# Expose port
EXPOSE 8000

# Command để chạy bot
CMD ["python", "discord_gemini_bot.py"]
