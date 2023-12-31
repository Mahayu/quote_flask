from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from flask_cors import CORS
import base64
from ocr_func import ocr_multiple_images
from typing import List, TypedDict

app = Flask(__name__)

CORS(app)
user = 'root'
password = 'Meina9758'
database = 'quote'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@10.1.0.110:3306/%s' % (user, password, database)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class quoteImage(db.Model):
    quote_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quote_desc = db.Column(db.String(255), nullable=False)
    quote_pic = db.Column(db.LargeBinary, nullable=False)
    quote_uuid = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.Date, nullable=False)


class quoteImageTp(TypedDict):
    quote_id: int
    quote_desc: str
    quote_pic: str
    quote_uuid: str
    upload_date: str


# form-data, key = files , value = blob
@app.route('/quote_upload', methods=['POST'])
def upload():
    try:
        files = request.files.getlist('files')
        if files:
            for file in files:
                if file:
                    quote_pic = file.read()
                    upload_file = quoteImage(quote_pic=quote_pic)
                    db.session.add(upload_file)
            db.session.commit()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'fail', 'error': 'No files uploaded'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'fail', 'error': str(e)})


# 根据UUID从中读取图片进行OCR
@app.route('/quote_ocr', methods=['POST'])
def ocr():
    try:
        data = request.get_json()
        if 'uuids' not in data:
            return jsonify({'error': 'uuids field is required'}), 400

        uuids = data['uuids']
        if not uuids:
            return jsonify({'message': 'No UUIDs provided'}), 400
        ocr_pic = 0
        ocr_items = []
        for uuid0 in uuids:
            record = quoteImage.query.filter_by(quote_uuid=uuid0).first()
            ocr_pic += 1
            if record:
                ocr_items.append([record.quote_pic, uuid0])
        ocr1 = ocr_multiple_images(ocr_items)
        # return jsonify({'message': f'{ocr_pic} pictures is processing'}), 200
        for quote_uuid, quote_desc in ocr1.items():
            record = quoteImage.query.filter_by(quote_uuid=quote_uuid).first()
            record.quote_desc = quote_desc
            db.session.commit()
        return jsonify({'message': f'{ocr_pic} pictures Processed'}), 200
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500


# 根据UUID删除图片,test_delete.json
@app.route('/quote_delete', methods=['POST'])
def delete_quote():
    try:
        data = request.get_json()
        if 'uuids' not in data:
            return jsonify({'error': 'uuids field is required'}), 400

        uuids = data['uuids']
        if not uuids:
            return jsonify({'message': 'No UUIDs provided'}), 400

        records_deleted = 0
        for uuid0 in uuids:
            record = quoteImage.query.filter_by(quote_uuid=uuid0).first()
            if record:
                db.session.delete(record)
                records_deleted += 1
        db.session.commit()
        return jsonify({'message': f'{records_deleted} records deleted successfully'}), 200
    except sqlalchemy.exc.SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500


# 获取未处理记录(上传页面,根据前端传来的分页返回数据）
@app.route('/get_todo_image', methods=['GET'])
def get_todo_image():
    number = int(request.args.get('number', 1))
    try:
        start_index = (number - 1) * 10
        end_index = start_index + 10
        records_without_quote_desc = quoteImage.query.filter(quoteImage.quote_desc.is_(None)).all()
        result_slice = [
            {
                'pic': base64.b64encode(record.quote_pic).decode('utf8'),
                'key': record.quote_uuid,
                'date': record.upload_date  # Add the 'date' field here
            }
            for record in records_without_quote_desc[start_index:end_index]
        ]

        return jsonify(result_slice), 200
    except Exception as e:
        error_message = 'An error occurred: ' + str(e)
        app.logger.error(error_message)  # Log the error message
        return jsonify({'error': error_message}), 500


# 获取未处理条目数，用于显示前端分页器
@app.route('/get_todo_number', methods=['GET'])
def get_todo_number():
    try:
        records_without_quote_desc = quoteImage.query.filter(quoteImage.quote_desc.is_(None)).all()
        result = len(records_without_quote_desc)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred'}, e), 500


@app.route('/get_todo_page', methods=['GET'])
def get_todo_page():
    try:
        records_without_quote_desc = quoteImage.query.filter(quoteImage.quote_desc.is_(None)).all()
        result = len(records_without_quote_desc)
        if result % 10 != 0:
            pages = result // 10 + 1
        else:
            pages = result // 10
        return jsonify(pages), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred'}, e), 500


# 获取全部记录（修改页面）
@app.route('/get_all_image', methods=['GET'])
def image():
    try:
        result = []
        records = quoteImage.query.all()
        for record in records:
            result.append({
                'desc': record.quote_desc,
                'pic': base64.b64encode(record.quote_pic).decode('utf8'),
                'key': record.quote_uuid,
                'date': record.quote_date
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500


if __name__ == '__main__':
    app.run()
