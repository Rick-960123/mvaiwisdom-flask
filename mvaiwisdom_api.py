from werkzeug.utils import secure_filename
from flask import request
from flask import Flask, jsonify, has_request_context, copy_current_request_context
from functools import wraps
from concurrent.futures import Future, ThreadPoolExecutor
from flask_cors import CORS
import time, os, random, asyncio, aiohttp
import mysql.connector

def run_async(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        call_result = Future()

        def _run():
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(func(*args, **kwargs))
            except Exception as error:
                call_result.set_exception(error)
            else:
                call_result.set_result(result)
            finally:
                loop.close()

        loop_executor = ThreadPoolExecutor(max_workers=10)
        if has_request_context():
            _run = copy_current_request_context(_run)
        loop_future = loop_executor.submit(_run)
        loop_future.result()
        return call_result.result()
    return _wrapper

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['JSONIFY_MIMETYPE'] ="application/json;charset=utf-8"
y, filename, filePath =  0, ['', '', '', ''], ['', '', '', '']

async def createdb(sel,val):
    conn = mysql.connector.connect(user='root', password='Aa-123456', database='mvai', use_unicode=True)
    cursor = conn.cursor()
    print(val)
    if sel == "news":
        cursor.execute(
            'insert into news (id,title,date,content,img,img1,img2,img3,url,url1,url2,url3,deletebit,listtype) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',val)
    if sel == "project":
        cursor.execute(
            'insert into project (id,name,author,date,img,img1,img2,img3,url,url1,url2,url3,deletebit,sort,source,link,patent_number,patent_copyright,patent_register,power_range,awardname,fjwork,listtype) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',val)
        
    if sel == "member":
        cursor.execute(
            'insert into member (id,name,admission_date,graduation_date,content,img,img1,img2,img3,url,url1,url2,url3,deletebit) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',val)

    conn.commit()
    cursor.close()
    return "r"
async def getdb(sel,val):
    conn = mysql.connector.connect(user='root', password='Aa-123456', database='mvai', use_unicode=True)
    cursor = conn.cursor()
    value=[val]
    print(value)
    if sel == "news":
        cursor.execute('select * from news where listtype=%s',value)
    if sel == "project":
        cursor.execute('select * from project where listtype=%s',value)
    if sel == "member":
        cursor.execute('select * from member')
    abc = cursor.fetchall()
    cursor.close()
    return abc
async def deletedb(sel,val):
    conn = mysql.connector.connect(user='root', password='Aa-123456', database='mvai', use_unicode=True)
    cursor = conn.cursor()
    if sel == "news":
        data = [val["deletebit"], val["title"], val["date"]]
        cursor.execute("update news set deletebit=%s where title=%s and date=%s", data)
    if sel == "project":
        data = [val["deletebit"], val["title"], val["date"]]
        cursor.execute("update project set deletebit=%s where name=%s and date=%s", data)
    if sel == "member":
        data = [val["deletebit"], val["title"], val["date"]]
        cursor.execute("update member set deletebit=%s where name=%s and admission_date=%s", data)
    conn.commit()
    cursor.close()
    return "r"
async def sa_im(file,name,y):
    global filename, filePath
    for f in file:
        creattime = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
        filename2 = secure_filename(f.filename)
        if len(filename2) < 5:
            filename1 = creattime+name+'.'+filename2
        elif len(filename2) > 15:
            filename1 = filename2
        else:
            filename1 = creattime+name+filename2
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(basepath, '../mvai/store', filename1)
        f.save(upload_path)
        filename[y] = f.filename
        filePath[y] = upload_path
        y = y+1
    print(filename)
    print(filePath)
    return "r"
@app.route('/getdata', methods=['GET'])
@run_async
async def getdata():
    sel = request.args.get('sel')
    if sel=="member":
        listtype=" "
    else:
        listtype = request.args.get('listtype')   
    abc = await getdb(sel,listtype)
    print(abc)
    return jsonify({
             "data": [d for d in abc],
                        }), 200
@app.route('/upload', methods=['POST'])
@run_async
async def upload_image():
    file = request.files.getlist('file')
    y = 0
    name = str(random.randint(0, 99))
    r = await sa_im(file,name,y)
    return jsonify({"res": True}), 200

@app.route('/delete', methods=['POST'])
@run_async
async def delete():
    value = {'date':0, 'title': 0, 'deletebit':0}
    sel = request.form['sel']
    value = request.form
    print(value)
    print(sel)
    r = await deletedb(sel,value)
    return jsonify({ "res": True }), 200

@app.route('/submit', methods=['POST'])
@run_async
async def submit():
    print(request.form)
    sel = request.form['sel']
    print(sel)
    global i,y ,filename, filePath
    if request.form['sel'] == "member":
        creattime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        value = [creattime,request.form['name'],request.form['admission_date'],request.form['graduation_date'],request.form['content'],filePath[0],filePath[1],filePath[2],filePath[3],filename[0],filename[1],filename[2],filename[3],"no"]
        r = await createdb(sel,value)
         
    if request.form['sel'] == "project":
        creattime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        value = [creattime,request.form['name'],request.form['author'],request.form['date'],filePath[0],filePath[1],filePath[2],filePath[3],filename[0],filename[1],filename[2],filename[3],"no",request.form['sort'],request.form['source'],request.form['link'],request.form['patent_number'],request.form['patent_copyright'],request.form['patent_register'],request.form['power_range'],request.form['awardname'],request.form['fjwork'],request.form['listtype']]
        print(value)
        r = await createdb(sel, value)
    if request.form['sel'] == "news":
        creattime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        value = [creattime,request.form['title'],request.form['date'],request.form['content'],filePath[0],filePath[1],filePath[2],filePath[3],filename[0],filename[1],filename[2],filename[3],"no",request.form['listtype']]
        r = await createdb(sel, value)
    filePath= ['','','','']
    filename= ['','','','']
    return jsonify({
                "res": True
            }), 200

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8012)