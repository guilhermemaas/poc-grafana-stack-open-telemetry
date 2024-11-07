FROM python:3.10-slim-buster

ENV APP_HOME=/home/app
RUN mkdir -p $APP_HOME
RUN groupadd app && useradd -g app app
WORKDIR $APP_HOME

COPY . .
RUN python -m pip install -r requirements.txt
RUN chown -R app:app $APP_HOME
USER app

EXPOSE 5000

CMD ["gunicorn", "--workers=1", "--bind", "0.0.0.0:5000", "--log-level=info", "app:app"]