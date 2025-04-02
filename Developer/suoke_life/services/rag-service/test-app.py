"""
简单的测试应用，用于验证RAG服务容器环境
"""

from flask import Flask, request, jsonify
import os
import sys
import platform

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "message": "索克生活测试服务运行正常",
        "service": "rag-service-test"
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'service': 'rag-service-test',
        'version': '1.0.0'
    })

@app.route('/system-info')
def system_info():
    installed_packages = []
    try:
        import pkg_resources
        installed_packages = sorted([f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set])
    except:
        installed_packages = ["无法获取已安装包信息"]
    
    return jsonify({
        "python_version": platform.python_version(),
        "system": platform.system(),
        "processor": platform.processor(),
        "env_vars": dict(os.environ),
        "installed_packages": installed_packages,
        "sys_paths": sys.path
    })

@app.route('/test-query', methods=['POST'])
def test_query():
    data = request.json or {}
    query = data.get('query', '默认查询')
    
    return jsonify({
        "query": query,
        "response": f"这是对'{query}'的测试响应。这表明RAG服务基本功能正常。",
        "sources": ["测试来源1", "测试来源2"]
    })

if __name__ == '__main__':
    # 获取环境变量PORT，如果不存在则使用8000
    port = int(os.environ.get('PORT', 8000))
    # 开启调试模式并监听所有接口
    app.run(host='0.0.0.0', port=port, debug=True) 