# RKSOK
**Final task of the "Basics of computer and web technologies with Python" 
course on stepik.org by Digitalize.**

---

The RKSOK protocol is the alternative for HTTP. The purpose of the protocol is 
to perform a phonebook. The RKSOK server communicates via TCP connection and reads data 
until `\r\n\r\n` (all responses also must end with this combination) or client 
disconnection. The protocol accepts the following raw structure of requests:

`COMMAND` `name` `PROTOCOL`\r\n`value`\r\n\r\n

The structure of responses:

`RESPONSE` `PROTOCOL`\r\n`value`\r\n\r\n (the rest after the first row is optional based
on `COMMAND` type).

Basically, the project allows you to use different versions of the RKSOK protocol. 
The file **service/protocols.py** includes the abstract class `RKSOKProtocol` which 
defines methods `_check_request_data`, `_format_response` and `process_request`.
In particular versions you have to implement methods `_get`, `_put`, `_delete` and 
class variable `configuration`. 

The project uses **MongoDB** as the main storage. However, there is a possibility to 
include another database, your variant just has to be inherited from `RKSOKDatabaseClient`
interface from the **service/db.py** file.

The RKSOK protocol also requires communication with the **Control Server**. The RKSOK 
server has to get a permission from the **Control Server** before responding to clients.
**Control Server** receives initial raw request and returns a permission answer. If request 
is accepted the RKSOK server will continue to process it. If request is not accepted the 
RKSOK server will return **Control Server**'s response directly to the client. Control server 
request format:

`ASK_COMMAND` `PROTOCOL`\r\n`request`\r\n\r\n

Responses
- `YES` `PROTOCOL`
- `NO` `PROTOCOL`\r\n`commentary`\r\n\r\n

---

The code only implements **RKSOK/1.0**. Commands:
- **ОТДОВАЙ** - method `get`, returns phone by name;
- **ЗОПИШИ** - method `put`, saves (name, phone) pair;
- **УДОЛИ** - method `delete`, deletes (name, phone) pair.

Available responses:
- **НОРМАЛДЫКС** - *OK* response;
- **НИНАШОЛ** - *NOT FOUND* response, when name was not found;
- **НИПОНЯЛ** - *INCORRECT* response, when request is incorrect.

Control server communication:
- **АМОЖНА?** - *ASK COMMAND*;
- **МОЖНА** - *YES* response;
- **НИЛЬЗЯ** - *NO* response

---

### Starting steps:

1. install MongoDB 6.0; 
2. install python>=3.10;
3. python -m pip install -r pip_requirements.txt (use virtual environment);
4. specify `RKSOK_SERVER_HOST`, `RKSOK_SERVER_PORT`, `MONGO_CONNECTION_URI` 
environmental variables;
5. run MongoDB on `MONGO_CONNECTION_URI`;
6. python server.py.