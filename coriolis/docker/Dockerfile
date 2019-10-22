FROM python:3.6

RUN pip install pyinstaller
ADD . /coriolis

WORKDIR /coriolis
RUN pip install -r requirements.txt
RUN pyinstaller --clean --onefile coriolis

FROM python:3.6

COPY --from=0 /coriolis/dist/coriolis /coriolis/
ENTRYPOINT ["/coriolis"]
