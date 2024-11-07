from flask import Flask
from time import sleep
import pyroscope

pyroscope.configure(
    application_name="lincros.pyroscope",
    server_address="http://pyroscope:4040"
)

app = Flask(__name__)

def task_cpu():
    for _ in range(10000000):
        pass

def task_memory():
    muita_memoria = [i for i in range(1000000)]
    sleep(2)

@app.route('/pyrescope')
def pyrescope():
    task_cpu()
    task_memory()
    return "teste!"

if __name__ == "__main__":
    app.run(debug=True, port=5008)