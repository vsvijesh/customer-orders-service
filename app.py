from flask import Flask
from prometheus_client import Counter, generate_latest

app = Flask(__name__)
request_count = Counter('request_count', 'Total request count')

@app.route('/')
def home():
    request_count.inc()
    return "Hello from customer-orders-service service!"

@app.route('/metrics')
def metrics():
    return generate_latest(), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
