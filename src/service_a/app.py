
from flask import Flask, jsonify, render_template, abort, json, request
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
#from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter #Exporter dos traces com gRCP
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from loguru import logger
import os
import requests

#Parâmetros das variáveis de ambiente
LOG_DIR = os.getenv('LOG_DIR')
SERVICE_B_URL = os.getenv('SERVICE_B_URL')
OTEL_TRACE_URL = os.getenv('OTEL_TRACE_URL')
OTEL_SERVICE_NAME = os.getenv('OTEL_SERVICE_NAME')

#Loguru
logger.remove()
logger.add(
    f"{LOG_DIR}/{OTEL_SERVICE_NAME}.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}",
    serialize=True,
    rotation="120 minutes",
    retention=3
)

#Configura para qualquer requests com a lib requests ser instrumentado pelo OpenTelemetry:
RequestsInstrumentor().instrument()

# Configure tracing
resource = Resource(attributes={
    SERVICE_NAME: OTEL_SERVICE_NAME
})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configura o OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint=f'{OTEL_TRACE_URL}'
)

# Adiciona processor de span
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

app = Flask(__name__)

# Instrumenta o Flask
FlaskInstrumentor().instrument_app(app)

#Gera endpoint /metrics Prometheus
metrics = PrometheusMetrics(app)

def get_trace_info(span):
    """
    Função para buscar o contexto atual (TracID e SpanID).
    """
    context = span.get_span_context()
    trace_id = format(context.trace_id, '032x')
    span_id = format(context.span_id, '016x')
    return trace_id, span_id


@app.route('/spans', methods = ['GET'])
def spans():
    """
    Request: http://service_b/spans
    """

    #with tracer.start_as_current_span("Sites Aleatórios"):
    #    response = requests.get('https://www.terra.com.br')

    response = requests.get(f'{SERVICE_B_URL}/spans')

    logger.info("Chamando serviço B", extra={"trace_id": format(trace.get_current_span().context.trace_id, '032x'), 
                                            "span_id": format(trace.get_current_span().context.span_id, '016x')})

    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Spans!</title>
        <style>
            body {
                background-color: #f0f0f5;
                font-family: 'Comic Sans MS', cursive, sans-serif;
            }
            h1 {
                color: red;
                font-size: 72px;
                text-align: center;
                margin-top: 20%;
            }
        </style>
    </head>
    <body>
        <h1>Spans!</h1>
    </body>
    </html>
    '''

@app.route('/lincros', methods = ['GET'])
def lincros():
    """
    Request: http://lincros.com
    """

    #with tracer.start_as_current_span("Sites Aleatórios"):
    #    response = requests.get('https://www.terra.com.br')

    response = requests.get('https://lincros.com')

    logger.info("Chamando serviço B", extra={"trace_id": format(trace.get_current_span().context.trace_id, '032x'), 
                                            "span_id": format(trace.get_current_span().context.span_id, '016x')})

    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Spans!</title>
        <style>
            body {
                background-color: #f0f0f5;
                font-family: 'Comic Sans MS', cursive, sans-serif;
            }
            h1 {
                color: red;
                font-size: 72px;
                text-align: center;
                margin-top: 20%;
            }
        </style>
    </head>
    <body>
        <h1>Spans!</h1>
    </body>
    </html>
    '''

@app.route('/erro', methods=['GET'])
def erro():
    """
    Request: http://lincros.com
    """
    try:
        # Simulando um erro: divisão por zero
        result = 1 / 0
    except Exception as e:
        logger.error("Erro ao processar a requisição", exc_info=True)

        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error!</title>
            <style>
                body {{
                    background-color: #f0f0f5;
                    font-family: 'Comic Sans MS', cursive, sans-serif;
                }}
                h1 {{
                    color: red;
                    font-size: 72px;
                    text-align: center;
                    margin-top: 20%;
                }}
            </style>
        </head>
        <body>
            <h1>Error Occurred!</h1>
        </body>
        </html>
        ''', 500

if __name__ == '__main__':
    app.run(debug=True, port=5005)