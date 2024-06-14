FROM python:latest

WORKDIR /dashboard

COPY requirements.txt .
RUN pip3 install -r requirements.txt 

EXPOSE 8501

COPY extract_bucket.py .
COPY main.py .


CMD ["streamlit", "run",  "main.py", "--server.port=8501"]