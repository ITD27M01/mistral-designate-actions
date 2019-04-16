# Prototype for mistal designate (v2 API) actions

Current implementation is based on designateclient but the future is openstacksdk.

## Installation

* Install package from pip:

```bash
    pip install mistral-designate-actions
```

* Populate the mistral database by new actions:

```bash
    mistral-db-manage --config-file /etc/mistral/mistral.conf populate &> mistral.log
```
 
* Check the population log (for example for designatev2 actions)

```bash
2019-04-16 17:43:43.308 37265 DEBUG mistral.services.action_manager [-]
    Registering action in DB: designatev2.recordset_create
```
