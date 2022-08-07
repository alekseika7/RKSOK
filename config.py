from os import path, getenv

SOURCE_DIR_PATH = path.dirname(path.abspath(__file__))

# Server conf
SERVER_HOST = getenv('RKSOK_SERVER_HOST')
SERVER_PORT = getenv('RKSOK_SERVER_PORT')
CLIENT_REQUEST_TIMEOUT = 30

# Control server conf
CONTROL_SERVER_HOST = 'vragi-vezde.to.digital'
CONTROL_SERVER_PORT = 51624

# DB conf
MONGO_CONNECTION_URI = getenv('MONGO_CONNECTION_URI')
MONGO_CONNECTION_MS_TIMEOUT = 15000
MONGO_DB_NAME = 'phone_numbers'

# Request processing conf
DB_QUERY_EXEC_TIMEOUT = 10
ENCODING = 'UTF-8'
READ_BLOCK_SIZE = 1024
REQUEST_END = '\r\n\r\n'
