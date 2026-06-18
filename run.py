import os
from waitress import serve
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"二次元交流站 - 生产模式启动")
    print(f"访问地址: http://0.0.0.0:{port}")
    serve(app, host='0.0.0.0', port=port, threads=8)
