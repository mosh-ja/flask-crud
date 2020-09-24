import os, logging
from flask import Flask
from db import db, migrate_db
from service import service
from common import BadRequest

log = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(service)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONN_STR')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate_db(app)


@app.errorhandler(BadRequest)
def handle_bad_request (error):
    return error.message, 400


def init_logging():
    log_level = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', level=log_level)

def main():
    init_logging()
    log.info('App started')
    app.run(host='0.0.0.0', port=5000, debug=log.level >= logging.DEBUG)
    
if __name__ == '__main__':
    main()