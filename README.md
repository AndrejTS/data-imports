# Data Imports

Tento projekt demonstruje proces importu dat s využitím API a Dockeru.

## Obsah

- [Diagramy](#diagramy)
- [Spuštění projektu](#spuštění-projektu)
- [API dokumentace](#api-dokumentace)
- [Uživatelé](#uživatelé)
- [Importy](#importy)

## Diagramy

### UML Diagram

![UML Diagram](https://github.com/AndrejTS/data-imports/blob/main/uml.png)

### Sekvenční diagram

![Sekvenční diagram](https://github.com/AndrejTS/data-imports/blob/main/uml_sek.png)

## Spuštění projektu

Projekt se spouští pomocí Docker Compose. Pro sestavení a spuštění použijte následující příkaz:

    docker-compose up --build

## API dokumentace

API je možné vyzkoušet prostřednictvím Swagger rozhraní, které najdete na adrese:

    http://localhost:8000/docs

## Uživatelé

V systému jsou k dispozici dva **dummy** uživatelé:

- **drone-user**
- **electro-user**

Heslo pro oba uživatele: `pass`

## Importy

### Automatický import

Pro uživatele `drone-user` je nastaven automatický import, který se spouští každých 15 sekund.

### Ruční spuštění importu

Import můžete spustit manuálně pomocí API volání. Příklad použití s **curl**:

    curl -X 'POST' \
      'http://localhost:8000/imports/start' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer electro-user' \
      -H 'Content-Type: application/json' \
      -d '{
      "website_id": "electronics-shop.com"
    }'

Tato dokumentace poskytuje základní informace potřebné k nasazení a vyzkoušení API. Pro další detaily a možnosti rozšíření doporučujeme prozkoumat Swagger rozhraní.
