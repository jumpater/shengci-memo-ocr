FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y expect
RUN apt-get update

#specify location to config timezone(Asia,Tokyo)
COPY tesseract-installation.exp /tmp
RUN expect /tmp/tesseract-installation.exp

RUN apt-get update
RUN apt-get install -y python3-pip tesseract-ocr tesseract-ocr-chi-sim
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
ADD ./webapp/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -q -r /tmp/requirements.txt
ADD ./webapp /opt/webapp/
WORKDIR /opt/webapp
RUN mkdir /var/log/gunicorn
RUN touch /var/log/gunicorn/gunicorn.log
RUN useradd admin
USER admin

# ↓for local debugging↓
# EXPOSE 8000
# CMD gunicorn --bind 0.0.0.0:8000 hanzi-ocr:app -w 2 -k uvicorn.workers.UvicornWorker --timeout 50\ 
# --access-logfile /var/log/gunicorn/gunicorn.log