FROM python:3.6
WORKDIR /project
COPY . .
RUN mkdir /input
RUN mkdir /output
RUN pip3 install -r requirements.txt
ENTRYPOINT entrypoint.sh
