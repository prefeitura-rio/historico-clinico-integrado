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