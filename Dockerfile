FROM python:latest
WORKDIR /myapp
ADD . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]