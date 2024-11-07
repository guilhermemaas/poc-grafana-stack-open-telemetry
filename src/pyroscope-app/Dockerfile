FROM python:3.10-slim-buster

ENV APP_HOME=/home/app
ENV LOG_DIR=/log

#RUN mkdir -p $APP_HOME
#RUN groupadd app && useradd -g app app

RUN mkdir -p $APP_HOME $LOG_DIR \
    && groupadd app \
    && useradd -g app app \
    && chown -R app:app $APP_HOME $LOG_DIR

WORKDIR $APP_HOME

COPY . .
RUN python -m pip install -r requirements.txt
RUN chown -R app:app $APP_HOME
USER app

#RUN mkdir -p $LOG_DIR && chown -R app:app $LOG_DIR

EXPOSE 5000

CMD ["gunicorn", "--workers=1", "--bind", "0.0.0.0:5000", "--log-level=info", "app:app"]