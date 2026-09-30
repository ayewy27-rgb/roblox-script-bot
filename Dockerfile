FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Hugging Face Spaces port
ENV PORT=7860
EXPOSE 7860

# Run bot
CMD ["python", "bot.py"]
