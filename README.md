# Azure Cosmos Db connect and cache method

[![Python][Python]][Python-url]
[![Azure][Azure]][Azure-url]
## Getting started
This classes are designed for a project with several request per second. That the reason for the cache and the singleton classes attach to the connection to CosmosDb. 
If you wan't only the connection with nothing else only copy the `cosmos_client.py` and change the setting to connect to your DB.

### Requirements
You'll need to have these available on your computer before running 
- Python >= 3.9
- [Virtualenv] (https://virtualenv.pypa.io/en/latest/installation.html)
- An Account in Azure or install a emulator to create the CosmosDb ( see section Azure Cosmos Db Emulator)

### Azure Cosmos Db Emulator

* Direct install
    ** For install directly in your computer, read this step by step by microsoft.
    https://learn.microsoft.com/en-us/azure/cosmos-db/local-emulator?tabs=ssl-netstd21

* Docker Container Install
    ** In the case that you want to use Docker to simulate your database
    https://github.com/Azure/azure-cosmos-db-emulator-docker

### Create a Cosmos Db in Azure
Follow the steps in the link below to create a CosmosDb in Azure.

https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/quickstart-portal

### Quick start
After creating the Db in Azure or installing the emulator, we can use the classes to connect to DB, just don't forget to change the configuration in the `cosmos_client.py`

```
HOST = ""
MASTERKEY = ""
DATABASEID = ""
```

Create virtual environment:
```bash
$ python -m venv env
```

Before doing anything, always make sure that you're in your local virtual environment:

```bash
$ source env/bin/activate
```

Install the python requirements:

```bash
$ pip install -r requirements.txt
```

To run the tests:
```bash
$ python -m pytest tests/
```


[Python]: https://img.shields.io/badge/python-20232A?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Azure]: https://img.shields.io/badge/azure-20232A?style=for-the-badge&logo=microsoft&logoColor=white
[Azure-url]: https://portal.azure.com/

