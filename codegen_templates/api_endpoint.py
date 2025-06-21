"""
Generated API endpoint: {{ endpoint_name }}
"""

from flask import Flask, request, jsonify
from typing import List, Dict, Any, Optional
import json


app = Flask(__name__)

# Mock database for demonstration
{{ endpoint_name }}_data = []


@app.route('/api/{{ endpoint_name }}', methods={{ methods | tojson }})
def {{ endpoint_name }}_endpoint():
    """
    {{ endpoint_name }} API endpoint supporting {{ methods | join(', ') }} methods.
    """
    {% for method in methods %}
    {% if method == "GET" %}
    if request.method == 'GET':
        return jsonify({
            'status': 'success',
            'data': {{ endpoint_name }}_data,
            'count': len({{ endpoint_name }}_data)
        })
    {% elif method == "POST" %}
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Validate required fields for {{ model_name }}
            required_fields = ['id', 'name']  # Customize based on your model
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Add to mock database
            {{ endpoint_name }}_data.append(data)
            return jsonify({
                'status': 'success',
                'message': '{{ model_name }} created successfully',
                'data': data
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    {% elif method == "PUT" %}
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            item_id = data.get('id')
            if not item_id:
                return jsonify({'error': 'ID is required for update'}), 400
            
            # Find and update item
            for i, item in enumerate({{ endpoint_name }}_data):
                if item.get('id') == item_id:
                    {{ endpoint_name }}_data[i] = data
                    return jsonify({
                        'status': 'success',
                        'message': '{{ model_name }} updated successfully',
                        'data': data
                    })
            
            return jsonify({'error': '{{ model_name }} not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    {% elif method == "DELETE" %}
    elif request.method == 'DELETE':
        try:
            item_id = request.args.get('id')
            if not item_id:
                return jsonify({'error': 'ID is required for deletion'}), 400
            
            # Find and delete item
            for i, item in enumerate({{ endpoint_name }}_data):
                if item.get('id') == item_id:
                    deleted_item = {{ endpoint_name }}_data.pop(i)
                    return jsonify({
                        'status': 'success',
                        'message': '{{ model_name }} deleted successfully',
                        'data': deleted_item
                    })
            
            return jsonify({'error': '{{ model_name }} not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    {% endif %}
    {% endfor %}
    
    return jsonify({'error': 'Method not allowed'}), 405


@app.route('/api/{{ endpoint_name }}/<item_id>', methods=['GET'])
def get_{{ endpoint_name }}_by_id(item_id):
    """
    Get specific {{ endpoint_name }} by ID.
    """
    for item in {{ endpoint_name }}_data:
        if item.get('id') == item_id:
            return jsonify({
                'status': 'success',
                'data': item
            })
    
    return jsonify({'error': '{{ model_name }} not found'}), 404


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 