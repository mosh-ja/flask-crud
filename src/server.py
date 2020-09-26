import os, logging, json
from flask import Flask, request
from werkzeug.exceptions import HTTPException
from db import db, init_db
from service import service


log = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(service)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONN_STR')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.errorhandler(HTTPException)
def handle_bad_request (error):
    return error.description, error.code

@app.after_request
def after_request(response):
    if log.level <= logging.DEBUG:
        try:
            log.debug({
                'request': {
                    'method': request.method,
                    'path': request.path,
                    'query_string': request.query_string
                },
                'response': {
                    'status_code': response.status_code,
                    'data': response.data
                }
            })
        except:
            pass
    return response


def init_logging():
    log_level = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(format='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s', level=log_level)

def main():
    init_logging()
    log.info('App started')
    db.init_app(app)
    init_db(app)
    app.run(host='0.0.0.0', port=5000, debug=log.level <= logging.DEBUG)
    
if __name__ == '__main__':
    main()