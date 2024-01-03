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

## Dados Iniciais
- Rode `python scripts/create_user.py --username pedro --password senha`


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


## Payloads para Testes

### Entidade `Patient` (Campos Obrigatórios)

```json
{
	"active": true,
	"birth_date": "1999-12-20",
	"gender": "male",
	"cpf": "11111111111",
	"name": "MANUEL GOMES",
   "telecom":  [{
      "value": "5521123456789"
   }]
}
```

### Entidade `Patient` (Todos os Campos)

```json
{
	"active": true,
   "address": [{
    	"use": "home",
    	"type": "physical",
    	"line": "AV SQN BLOCO M 604 APARTAMENTO ASA NORTE",
    	"city": "Rio de Janeiro",
    	"state": "Rio de Janeiro",
    	"postal_code": "70752130",
    	"period": {
    		"start": "2020-10-01 00:00:00",
    		"end": "2020-10-02 00:00:00"
    		}
    	}],
   "birth_city": "Rio de Janeiro",
	"birth_country": "Brasil",
	"birth_date": "1999-12-20 00:00:00",
	"deceased": false,
	"gender": "male",
	"cpf": "12345678901",
	"cns": "1234567890000000",
	"name": "GABRIELA INACIO ALVES",
	"nationality": "B",
	"naturalization": "",
	"mother": "MARILIA FARES DA ROCHA ALVES",
	"father": "JURACY ALVES",
	"protected_person": false,
	"race": "Parda",
	"ethnicity": "PATAXO",
	"telecom":  [{
		"system": "phone",
		"use": "home",
      	"value": "5521123456789",
      	"rank": "1",
      	"period": {
      		"start": "2020-10-01 00:00:00",
    		"end": "2020-10-02 00:00:00"
    		}
    	}]
}
```