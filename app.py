from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from flask_cors import CORS
import base64
from ocr_func import ocr_multiple_file

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
                ocr_items.append(record.quote_pic)
        ocr = ocr_multiple_file(ocr_items)
        return jsonify({'message': f'{ocr_pic} pictures is processing'}), 200
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


# 获取未处理记录(上传页面）
@app.route('/get_todo_image', methods=['GET'])
def get_todo_image():
    try:
        records_without_quote_desc = quoteImage.query.filter(quoteImage.quote_desc.is_(None)).all()
        result = [{'pic': base64.b64encode(record.quote_pic).decode('utf8'), 'uuid': record.quote_uuid} for record in
                  records_without_quote_desc]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500


# 获取全部记录（修改页面）
@app.route('/get_all_image', methods=['GET'])
def image():
    try:
        result = []
        records = quoteImage.query.all()
        for record in records:
            result.append({
                'quote_desc': record.quote_desc,
                'quote_pic': base64.b64encode(record.quote_pic).decode('utf8'),  # 解决编码问题
                'quote_uuid': record.quote_uuid  # 如果要返回quote_uuid字段，使用record.uuid
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500


if __name__ == '__main__':
    app.run()
