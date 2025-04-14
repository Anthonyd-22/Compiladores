import os
import jwt
import requests
from flask import Flask, request, redirect, render_template, make_response, url_for, jsonify, Response
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
SECRET_KEY = os.getenv('SECRET_KEY')
API_BASE_URL = os.getenv("API_BASE_URL")

@app.route('/')
def home():
    token = request.cookies.get('access_token')
    user_role = request.cookies.get('user_role')
    if not token:
        return redirect(url_for('login'))
    return render_template('index.html', user_role=user_role)

@app.route('/login')
def login():
    return render_template('sign_in.html')

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('access_token')
    response.delete_cookie('user_role')
    return response

@app.route('/set_cookies', methods=['POST'])
def set_cookies():
    try:
        data = request.get_json()
        token = data.get('token')
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('access_token', token, httponly=True)
        resp.set_cookie('user_role', payload['role'], httponly=True)
        return resp
    except jwt.InvalidTokenError:
        return jsonify({"error": "Access cannot be granted without a valid token"}), 403


@app.route('/api_proxy/<path:subpath>', methods=['GET', 'POST', 'DELETE'])
def api_proxy(subpath):
    token = request.cookies.get('access_token')
    if not token:
        return jsonify({"error": "No token found in cookies"}), 403

    headers = {
        'Authorization': f'Bearer {token}'
    }

    method = request.method
    url = f"{API_BASE_URL}/{subpath}"
    data = request.get_json(silent=True)
    params = request.args

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params
        )

        # Reenviar la respuesta original (status y contenido)
        return Response(response.content, status=response.status_code, content_type=response.headers.get('Content-Type'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
