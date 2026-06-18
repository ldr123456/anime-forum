from waitress import serve
from app import app

if __name__ == '__main__':
    print("二次元交流站 - 生产模式启动")
    print("访问地址: http://localhost:5000")
    serve(app, host='0.0.0.0', port=5000, threads=8)
