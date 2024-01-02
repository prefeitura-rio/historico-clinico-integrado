# FHIR

## Setup

- Garanta instalação de Docker e Docker Compose
- Configure em `docker-compose.yaml` a variável `ENVIRONMENT` para `dev` ou `prod`
   - `dev`: Ambiente de Desenvolvimento
   - `prod`: Ambiente de Produção
- Rode `docker compose up --build` na raiz do projeto
- Os serviços estão definidos em:

|Serviço|URL|Porta|Usuário|Senha|
|--|--|--|--|--|
|Banco de Dados (Postgres) |localhost|8001|postgres|postgres|
|API (Fast API) | localhost|8000|-|-|