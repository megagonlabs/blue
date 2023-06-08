FROM python:3.9

MAINTAINER Eser Kandogan "eser@megagon.ai"

# Set workdir
WORKDIR .

# Build requirements first
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy service files
ADD /src .

ENTRYPOINT [ "python" ]

CMD [ "service.py" ]
