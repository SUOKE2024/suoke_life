from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
CORS(app)

request_count = Counter('llm_requests_total', 'Total number of LLM requests')
request_latency = Histogram('llm_request_latency_seconds', 'Latency of LLM requests')

@app.route('/llm/generate', methods=['POST'])
def generate_text():
    start_time = time.time()
    request_count.inc()
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # Simulate LLM processing time
    time.sleep(2)
    
    response = f"AI response to: {prompt}"
    end_time = time.time()
    request_latency.observe(end_time - start_time)
    return jsonify({'text': response})

app_dispatch = DispatcherMiddleware(app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app_dispatch) 