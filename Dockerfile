FROM python:3.9-slim

ENV USER=eventgen
ENV UID=12345
ENV GID=23456
ENV PATH="/home/${USER}/local/bin:${PATH}"

RUN addgroup \
    --gid "$GID" \
    "$USER"

RUN mkdir /out
RUN mkdir /logs

RUN chown ${UID}:${GID} /out
RUN chown ${UID}:${GID} /logs

RUN adduser \
    --disabled-password \
    --gecos "" \
    --ingroup "$USER" \
    --uid "$UID" \
    "$USER"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
        git

USER $USER
RUN pip install --no-warn-script-location --user https://github.com/splunk/eventgen/archive/7.2.0.tar.gz

WORKDIR /repo
COPY bundles ./bundles

COPY entrypoint.sh ./entrypoint.sh
USER root
RUN chmod +x entrypoint.sh
USER $USER

ENV BUNDLE_DIR=/bundle
ENV EVENTGEN_LOG_DIR=/logs

ENTRYPOINT ["/repo/entrypoint.sh"]
CMD ["/bundle/" ]