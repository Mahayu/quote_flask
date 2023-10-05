import os
import uuid
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import send_file, make_response

app = Flask(__name__)

CORS(app)
user = 'root'
password = 'Meina9758'
database = 'quote'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@nj1.bridgecn.top:3306/%s' % (user, password, database)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


class QuoteData(db.Model):
    quote_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quote_blob = db.Column(db.String(255), nullable=False)
    quote_desc = db.Column(db.String(255), nullable=False)


'''
class Cut(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pic = db.Column(db.LargeBinary)
    pic_cut = db.Column(db.LargeBinary)
    pic_uuid = db.Column(db.String(255))

    def __init__(self, pic, pic_uuid):
        self.pic = pic
        self.pic_uuid = pic_uuid
'''


@app.route('/upload_quote', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        '''
        pic_data = file.read()
        uuid_str = str(uuid.uuid4())
        upload_file = Cut(pic=pic_data, pic_uuid=uuid_str)
        db.session.add(upload_file)
        db.session.commit()
        '''
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'fail', 'error': '上传失败'})


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
