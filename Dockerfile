FROM alpine

ARG APP_VERSION=?
ENV APP_VERSION=$APP_VERSION
ENV APPDIR=/srv/jobserv
ENV PYTHONPATH=$APPDIR
ENV FLASK_APP=jobserv.app:app

# Setup flask application
RUN mkdir -p $APPDIR
COPY ./ $APPDIR/

RUN apk --no-cache add python3 py3-pip mysql-client python3-dev musl-dev gcc openssl libffi-dev openssl-dev && \
	pip3 install --upgrade pip setuptools && \
	pip3 install -r $APPDIR/requirements.txt && \
	cd $APPDIR/runner && python3 ./setup.py bdist_wheel && \
	apk del python3-dev musl-dev gcc libffi-dev openssl-dev

WORKDIR $APPDIR
EXPOSE 8000

# Start gunicorn
CMD ["/srv/jobserv/docker_run.sh"]
