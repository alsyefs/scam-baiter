from flask import Blueprint, Response, render_template, request, redirect, url_for, session, flash, jsonify
import json
from backend.database.models import db_models, User, Role
from logs import LogManager
log = LogManager.get_logger()
import traceback
from functools import wraps
from datetime import datetime
import openai
import re
from globals import OPENAI_API_KEY, GPT_MODEL
from database.gpt_table import GPTDatabaseManager

openai.api_key = OPENAI_API_KEY
gpt_bp = Blueprint('gpt', __name__)
users_bp = Blueprint('users', __name__)
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('You need to be signed in to view this page.', 'error')
                return redirect(url_for('users.signin'))
            current_user = User.query.filter_by(username=session['username']).first()
            if current_user:
                user_roles = [role.name for role in current_user.roles]
                if any(role in roles for role in user_roles):
                    return f(*args, **kwargs)
            flash('You do not have the required permissions to view this page.', 'error')
            return redirect(url_for('index'))
        return decorated_function
    return wrapper

def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()
    
@gpt_bp.route('/gpt')
@requires_roles('admin', 'super admin', 'user')
def index():
    user_roles = []
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_roles = [role.name for role in user.roles]
    return render_template('gpt.html', user_roles=user_roles)

def generate_gpt_text(gpt_instructions, prompt_message, gpt_model=GPT_MODEL, temperature=0.2, max_length=4000, stop=None, top_p=0.2, presence_penalty=0.5, frequency_penalty=0.5):
    max_length = int(max_length)
    temperature = float(temperature)
    top_p = float(top_p)
    presence_penalty = float(presence_penalty)
    frequency_penalty = float(frequency_penalty)
    messages = [
        {"role": "system", "content": gpt_instructions},
        {"role": "user", "content": prompt_message}
    ]
    request_params = {
            "messages": messages,
            "model": gpt_model,
            "temperature": temperature,
            "max_tokens": max_length,
            "top_p": top_p,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty
            }
    if stop:
        request_params["stop"] = stop
    try:
        log.info(f"Generating text with the following parameters: {messages}, {gpt_model}, {temperature}, {max_length}, {stop}, {top_p}, {presence_penalty}, {frequency_penalty}")
        completion = openai.ChatCompletion.create(**request_params)
        log.info(f"Generated text: {completion.choices[0].message['content']}")
        return completion.choices[0].message['content']
    except Exception as e:
        log.error(f"Error: {e}")
        return None
    
@gpt_bp.route('/generate_text', methods=['POST'])
@requires_roles('admin', 'super admin', 'user')
def generate_text():
    try:
        data = request.json
        gpt_instructions = data.get('system_instructions')
        prompt_message = data.get('user_input')
        gpt_model = data.get('model')
        temperature = data.get('temperature')
        max_length = data.get('max_length')
        stop_sequences = data.get('stop_sequences', [])
        top_p = data.get('top_p')
        presence_penalty = data.get('presence_penalty')
        frequency_penalty = data.get('frequency_penalty')
        response = generate_gpt_text(
            gpt_instructions=gpt_instructions,
            prompt_message=prompt_message,
            gpt_model=gpt_model,
            temperature=temperature,
            max_length=max_length,
            stop=stop_sequences if stop_sequences else None,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty
        )
        GPTDatabaseManager.insert_gpt(
            prompt=prompt_message,
            generated_text=response,
            instructions=gpt_instructions,
            model=gpt_model,
            temperature=temperature,
            max_length=max_length,
            stop_sequences=','.join(stop_sequences) if stop_sequences else None,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            username=session.get('username')
        )
        return jsonify({'response': response})
    except Exception as e:
        log.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@gpt_bp.route('/gpt_interactions', methods=['GET'])
@requires_roles('admin', 'super admin')
def gpt_interactions():
    try:
        user_roles = []
        if 'username' in session:
            user = User.query.filter_by(username=session['username']).first()
            if user:
                user_roles = [role.name for role in user.roles]
        return render_template('gpt_interactions.html', user_roles=user_roles)
    except Exception as e:
        log.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    
@gpt_bp.route('/select_all_gpt_interactions')
@requires_roles('admin', 'super admin')
def select_all_gpt_interactions():
    gpts = GPTDatabaseManager.get_gpts()
    return jsonify([dict(gpt) for gpt in gpts])
