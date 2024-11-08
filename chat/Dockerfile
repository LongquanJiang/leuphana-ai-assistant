FROM python:3.9

RUN mkdir /app

WORKDIR /app

COPY ./src ./

COPY requirements.txt ./

RUN mkdir /data

COPY ./data /data/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py", "runserver", "0.0.0.0:30003"]