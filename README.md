# Histórico Clínico Integrado
- Responsável de Infraestrutura: Gabriel Milan (Escritório de Dados)
- Administrador: Pedro Marques (DIT @ SMS)

## O que é o HCI?
- O HCI tem como objetivo integrar os dados de saúde municipais de diferentes unidades de saúde, seja da atenção primária, hospitalar, etc.
- Existem diferentes tipos de prontuário sendo utilizados nas unidades, o que faz com que existem diferentes fonte, com formatos e dados diferentes.
- Precisamos ler dados destas fontes e integrá-los em um formato consistente, que atenda os profissionais da área de saúde.

### O Sistema
- O HCI possui dois componentes:
   - API (desenvolvida em Fast API, Python 3.11); e
   - Banco de Dados (PostgreSQL).

## Preparação de Ambiente
- Comece rodando `pre-commit install` na raiz do repositório.
- O projeto da API está na pasta `api/` e esta será a pasta raiz de **agora em diante**
- Dentro da raiz, crie um arquivo `.env` e nele defina duas variáveis de ambiente:
   - Peça ao Administrador mais informações sobre seus valores.
```
INFISICAL_ADDRESS=<Endereço do Servidor Infisical>
INFISICAL_TOKEN=<Token do projeto>
```
- Garanta instalação do poetry e pyenv com python 3.11
- Crie um ambiente poetry *dentro do projeto*.
   - Por padrão, o poetry armazena os arquivos do ambiente fora do projeto.
   - Neste caso, para facilitar a configuração da depuração, iremos configurar para salvar os arquivos em uma pasta `.venv` na raiz do projeto.
   - Rode: `poetry config virtualenvs.in-project true`
   - Se já tinha um ambiente, remova com `poetry env remove <ID_DO_ENV>` e inicie um novo ambiente
- Na pasta raiz, rode `poetry shell` e depois `poetry install`
- Garanta instalação de Docker e Docker Compose

## Rodando com Docker (BD e/ou API)
- **Localização**: esteja na pasta raiz
- **Rode os comandos**:
  - Para subir a API **e** o banco de dados, rode `docker compose up --build`
  - Para subir **apenas o banco de dados**: `docker compose up db --build`
- Os serviços ficam disponíveis em:

|Serviço|URL|Porta|Usuário|Senha|
|--|--|--|--|--|
|Banco de Dados (Postgres) |localhost|5432|postgres|postgres|
|API (Fast API) | localhost |**8000**|-|-|

### Rodando com Debugger (Apenas API)
- **Subindo o banco**: rode `docker compose up db --build` para subir apenas o banco de dados local.
- **Inicie a depuração**: o VSCode detecta automaticamente o arquivo que configura a depuração. Basta dar "play" na aba de depuração
- O serviço fica disponível em:

|Serviço|URL|Porta|Usuário|Senha|
|--|--|--|--|--|
|API (Fast API) | localhost |**8001**|-|-|

## Testes Automatizados
- Os testes estão definidos na pasta `api/tests/`
- Para rodar os testes basta executar no terminal `pytest --disable-warnings`.
