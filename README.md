# Prontuários Integrados API

## Preparação de Ambiente
- Rode `pre-commit install`
- O projeto está na pasta `api/`
- Para rodar o banco de dados é obrigatório utilizar um ambiente virtual docker
- Para rodar a API você pode optar pelo docker ou pelo ambiente

### Utilizando Docker (BD e API)
*Ideal para deploy e subir o banco de dados localmente*

- Esteja na pasta `./api/`
- Garanta instalação de Docker e Docker Compose
- Configure em `docker-compose.yaml` a variável `ENVIRONMENT` para `dev` ou `prod`
   - `dev`: Ambiente de Desenvolvimento
   - `prod`: Ambiente de Produção
- Para subir a API e o banco de dados, rode `docker compose up --build`
- Se quiser subir apenas o banco de dados: `docker compose up db --build`
- Os serviços ficam disponíveis em:

|Serviço|URL|Porta|Usuário|Senha|
|--|--|--|--|--|
|Banco de Dados (Postgres) |localhost|5432|postgres|postgres|
|API (Fast API) | localhost|**8000**|-|-|

### Utilizando Poetry (Apenas API)
*Ideal para debugging da API e execução de testes localmente*
- Na pasta `./api/` rode `poetry shell` e depois `poetry install`
- Para inicializar a API rode: `uvicorn app.main:app --host 0.0.0.0 --port 8001`
   - PS.: Recomendado seguir o tutorial de Debugging e executar por lá.
- O serviço estará disponivel em:

|Serviço|URL|Porta|Usuário|Senha|
|--|--|--|--|--|
|API (Fast API) | localhost|**8001**|-|-|


## Dados Iniciais
- Dois scripts que populam o banco com dados iniciais:
  - Crie um usuário próprio: `python scripts/create_user.py --username <USUARIO> --password <SENHA>`
  - Crie dados iniciais: `python scripts/database_initial_data.py`
- **Atenção**: Caso precise limpar todos os dados do banco: `python scripts/database_cleanup.py`

## Testes Automatizados

- Os testes estão definidos na pasta `api/tests/`
- Para rodar os testes basta executar no terminal `pytest --disable-warnings`

## Debugging
- Para fazer o debugging da API você vai rodá-la fora do container docker. Dessa forma a configuração é simples.
- Arquivos de configuração disponíveis em `.vscode/launch.json`.

### Setup
- **Suba o container**: rode `docker compose up` para subir o banco de dados.
- **Crie um ambiente virtual**: crie um ambiente poetry *dentro do projeto*.
   - Por padrão, o poetry armazena os arquivos do ambiente fora do projeto.
   - Neste caso, para facilitar a configuração da depuração, iremos configurar para salvar os arquivos em uma pasta `.venv` na raiz do projeto.
   - Rode: `poetry config virtualenvs.in-project true`
   - Se já tinha um ambiente, remova com `poetry env remove <ID_DO_ENV>` e inicie um novo ambiente

### Uso
- **Inicie a depuração**: o VSCode detecta automaticamente o arquivo que configura a depuração. Basta dar "play" na aba de depuração
- O serviço fica disponível em:

|Serviço|URL|Porta|Usuário|Senha|
|--|--|--|--|--|
|API (Fast API) | localhost|**8001**|-|-|