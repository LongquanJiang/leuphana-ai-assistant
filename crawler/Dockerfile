FROM python:3

RUN mkdir /app

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

RUN mkdir /data

COPY ./src /app

# Run the crawler when the container launches.
CMD [ "python3", "./go-spider.py" ]