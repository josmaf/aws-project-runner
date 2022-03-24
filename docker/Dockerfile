FROM python:3.6
WORKDIR /project
COPY . .
RUN ["chmod", "+x", "/project/entrypoint.sh"]
RUN mkdir /input
RUN mkdir /output
RUN pip3 install -r requirements.txt
ENTRYPOINT ["/project/entrypoint.sh"]
