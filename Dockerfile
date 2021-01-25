FROM python

RUN pip3 install discord youtube_dl pynacl python-dotenv requests

ENTRYPOINT ["/bin/bash"]