from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import random
import time
import logging
import os
import pika
import pymongo
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.pika import PikaInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from pythonjsonlogger import jsonlogger

#Busca configurações das variáveis de ambiente
LOG_DIR = os.getenv('LOG_DIR')
OTEL_TRACE_URL = os.getenv('OTEL_TRACE_URL')
OTEL_SERVICE_NAME = os.getenv('OTEL_SERVICE_NAME')
RABBIT_HOST = os.getenv('RABBIT_HOST')
MONGO_HOST = os.getenv('MONGO_HOST')

# Configura o logging
log_dir = LOG_DIR
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'posicoes.log')

log_handler_console = logging.StreamHandler()
log_handler_file = logging.FileHandler(log_file)
formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(message)s %(trace_id)s %(span_id)s %(name)s'
)

log_handler_console.setFormatter(formatter)
log_handler_file.setFormatter(formatter)

logger = logging.getLogger('json_logger')
logger.addHandler(log_handler_console)
logger.addHandler(log_handler_file)
logger.setLevel(logging.INFO)


#Configurar trace
resource = Resource(attributes={
    SERVICE_NAME: OTEL_SERVICE_NAME
})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configura o OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint=OTEL_TRACE_URL
)

trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

app = Flask(__name__)

# Auto instrumentação para Flask, Pika e Pymongo
FlaskInstrumentor().instrument_app(app)
PymongoInstrumentor().instrument()
PikaInstrumentor().instrument()

#Gera endpoint /metrics Prometheus
metrics = PrometheusMetrics(app)

def gerar_posicao_random():
    lat = random.uniform(-90, 90)
    long = random.uniform(-180, 180)
    cliente_placa = random.choice([
        {'cliente': 'XYZ', 'placa': 'ABC123'},{'cliente': 'Panco', 'placa': 'YHG4335'},
        {'cliente': 'XYZ', 'placa': 'DFE321'},{'cliente': 'Panco', 'placa': 'HXE4625'},
        {'cliente': 'XYZ', 'placa': 'XYX431'},{'cliente': 'MetalFrio', 'placa': 'HAE6325'},
        {'cliente': 'XYZ', 'placa': 'HGE435'},{'cliente': 'MetalFrio', 'placa': 'RRE4645'},
        {'cliente': 'XPTO', 'placa': 'RGH321'},{'cliente': 'MetalFrio', 'placa': 'HGH325'},
        {'cliente': 'XPTO', 'placa': 'IKL135'},{'cliente': 'MetalFrio', 'placa': 'HJR4355'},
    ])
    tipo = random.choice(['entrega', 'devolucao', 'reversao'])
    return {'lat': lat, 'long': long, 'cliente': cliente_placa['cliente'], 
            'placa': cliente_placa['placa'], 'tipo': tipo}


def valida_posicao():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("valida_lat_long_validas") as span:
        span.add_event("OK - Latitude e longitude são válidos.")
    with tracer.start_as_current_span("valida_posicao_duplicada") as span:          
        time.sleep(random.uniform(0.1, 0.3))
        client = pymongo.MongoClient(f"mongodb://{MONGO_HOST}:27017/")
        db = client["posicoes_db"]
        collection = db["posicoes"]
        resultado = collection.find_one({"placa": "ABC123"})  # Exemplo de consulta no MongoDB
        span.add_event("Posição não existe na base, e será inserida.")
    return random.choice([True, False])


def publica_posicao(posicao):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("publica_rabbit") as span:
        time.sleep(random.uniform(0.1, 0.3))
        span.set_attribute("messaging.system", "rabbitmq")
        span.set_attribute("operation", "publish")
        span.set_attribute("vhost","/")
        span.set_attribute("queue", "posicao")

        connection = pika.BlockingConnection(pika.ConnectionParameters(f'{RABBIT_HOST}'))
        channel = connection.channel()
        channel.queue_declare(queue='posicoes')
        channel.basic_publish(exchange='',
                                routing_key='posicoes',
                                body=str(posicao))
        connection.close()

        span.add_event(f"""
                       Publicação de posição no RabbitMQ realizada: {posicao['cliente']}/{posicao['placa']}/{posicao['lat']},{posicao['long']}
                       """)        


@app.route('/posicoes', methods = ['GET'])
def posicoes():

    with tracer.start_as_current_span('processa_posicao') as span:
        posicao = gerar_posicao_random()

        span.add_event(f"""
                       Posição recebida: {posicao['cliente']}/{posicao['placa']}/{posicao['lat']},{posicao['long']}.
                       Iniciando processamento da ocorrência.
                       """)     
    
        span.set_attribute('lincros.posicao.cliente', posicao['cliente'])
        span.set_attribute('lincros.posicao.placa', posicao['placa'])
        span.set_attribute('lincros.posicao.tipo_posicao', posicao['tipo'])
        
        with tracer.start_as_current_span('valida_posicao') as span:
            span.add_event("Iniciando validação da posição.")

            valida_posicao()

        falha = random.choice([True, False, False, False])

        if falha:
            response = jsonify({'error': 'Erro ao processar posicao.'}), 500
            logger.error("Erro ao processar posicao.", extra={
                'cliente': posicao['cliente'],
                'placa': posicao['placa'],
                'tipo_posicao': posicao['tipo'],
                'trace_id': span.get_span_context().trace_id,
                'span_id': span.get_span_context().span_id
            })
        else:
            response = jsonify(posicao)
            logger.info("Posicao recebida.", extra={
                'cliente': posicao['cliente'],
                'placa': posicao['placa'],
                'tipo_posicao': posicao['tipo'],
                'trace_id': span.get_span_context().trace_id,
                'span_id': span.get_span_context().span_id
            })

            publica_posicao(posicao)

        time.sleep(random.uniform(0.1, 3))

        span.add_event("Finalizado importação da posição.")

    return response

if __name__ == '__main__':
    app.run(debug=False, port=5006)
