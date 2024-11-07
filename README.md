# Como rodar localmente:

### Clonar o repositório:
`git clone git@ssh.dev.azure.com:v3/lincros-sa/DevOps%20and%20SRE/poc-grafana-stack`

### Iniciar os containers:
`docker compose -f docker-compose.yaml up --build -d`

Ao rodar esse comando os seguintes containers serão iniciados:

### Aplicações:
service_a, service_b, service_c, posicoes, piroscope-app

### Grafana Stack:
grafana-tempo, grafana-loki, grafana-agent, grafana e pyroscope

### Prometheus:
prometheus, alert-manager

### Minio (S3):
minio, minio-create-bucket (Container temporário, após criar os buckets ele é finalizado.)

Observação: Caso não queira subir algum container específico, basta editar o arquvio docker-compose.yaml, na raíz do projeto, e remover ou comentar as linhas dos serviços em questão.

# Como enviar Traces para o Grafana Tempo, ou Grafana Agent:

No seu código, basta apontar a URL abaixo para envio de traces:

### Grafana Agent:
`http://grafana-agent:4318/v1/traces` 

ou, caso esteja rodando a aplicação localmente (sem buildar um container):

`http://localhost:4328/v1/traces`

### Grafana Tempo diretamente:
`http://grafana-tempo:4318/v1/traces`

ou, caso esteja rodando a aplicação localmente (sem buildar um container):

`http://localhost:4318/v1/traces`

Obs.: Após isso, basta acessar o Grafana, e através do menu "Explore" selecionar o Data Source do Tempo e visualisar os Traces.

# Como acessar o Grafana para visualizar traces, logs e métricas, Prometheus, Alert Manager e o Minio:

Grafana:
Usuário: Admin, Senha: admin
`http://localhost:3000`

Prometheus:
`http://localhost:9090`

Alert Manager:
`http://localhost:9093`

Minio:
Usuário: minioadmin, Senha: minioadmin
`http://localhost:9001/buckets`


# Como gerar traces e logs para visualização utilizando os apps service_a/b/c e posicoes:

### service_a:

Basta chamar no navegador a seguinte URL:

`http://localhost:5000/spans`

### Posições:

Basta rodar o comando abaixo em um terminal com bash para simular as chamadas:

`while true; do   curl http://localhost:5005/posicoes;   echo "";   sleep 0.5; done`

Obs.: Após isso, basta acessar o Grafana, e através do menu "Explore" selecionar o Data Source do Tempo e visualisar os Traces.