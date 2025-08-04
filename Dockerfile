FROM python:3.13-alpine

WORKDIR /app
COPY fakesmtp.py .

EXPOSE 25

CMD ["python", "fakesmtp.py"]
