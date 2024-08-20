from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.DEBUG)

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('./zomato.db')
    conn.row_factory = sqlite3.Row
    return conn

# Root endpoint to check if server is running
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

# Endpoint to get restaurant details by ID
@app.route('/restaurants/<int:id>', methods=['GET'])
@app.route('/api/restaurants/<int:id>', methods=['GET'])
def restaurant_details(id):
    try:
        conn = get_db_connection()
        app.logger.debug(f"Getting details for restaurant with ID: {id}")
        restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', (id,)).fetchone()
        conn.close()
        
        if restaurant is None:
            app.logger.debug(f"Restaurant with ID: {id} not found")
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Restaurant not found'}), 404
            return render_template('error.html', message='Restaurant not found'), 404
        
        app.logger.debug(f"Restaurant found: {restaurant}")
        if request.path.startswith('/api/'):
            return jsonify(dict(restaurant))
        return render_template('restaurant_detail.html', restaurant=restaurant)
    except Exception as e:
        app.logger.error(f'Error occurred: {e}')
        if request.path.startswith('/api/'):
            return jsonify({'error': str(e)}), 500
        return render_template('error.html', message=f"An error occurred: {str(e)}"), 500

# Endpoint to get list of restaurants with pagination and render the list template
@app.route('/restaurants', methods=['GET'])
@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    try:
        conn = get_db_connection()

        # Retrieve parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        ratings = request.args.getlist('rating')
        country = request.args.get('country', '')
        average_cost = request.args.get('average_cost', '')
        cuisines = request.args.getlist('cuisines')

        offset = (page - 1) * per_page

        # Build query
        query = 'SELECT * FROM restaurants WHERE 1=1'
        params = []

        if search:
            query += ' AND name LIKE ?'
            params.append(f'%{search}%')

        if ratings:
            query += ' AND aggregate_rating IN (' + ','.join(['?'] * len(ratings)) + ')'
            params.extend(ratings)

        if country:
            query += ' AND country = ?'
            params.append(country)

        if average_cost:
            if average_cost == "<20":
                query += ' AND average_cost_for_two < 20'
            elif average_cost == "20-50":
                query += ' AND average_cost_for_two BETWEEN 20 AND 50'
            elif average_cost == "50-500":
                query += ' AND average_cost_for_two BETWEEN 50 AND 100'
            elif average_cost == ">1000":
                query += ' AND average_cost_for_two > 100'

        if cuisines:
            query += ' AND (' + ' OR '.join(['cuisines LIKE ?'] * len(cuisines)) + ')'
            params.extend([f'%{cuisine}%' for cuisine in cuisines])

        query += ' LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        # Execute query
        restaurants = conn.execute(query, params).fetchall()

        # Calculate total pages for pagination
        total_query = 'SELECT COUNT(*) FROM restaurants WHERE 1=1'
        total_params = []

        if search:
            total_query += ' AND name LIKE ?'
            total_params.append(f'%{search}%')

        if ratings:
            total_query += ' AND aggregate_rating IN (' + ','.join(['?'] * len(ratings)) + ')'
            total_params.extend(ratings)

        if country:
            total_query += ' AND country = ?'
            total_params.append(country)

        if average_cost:
            if average_cost == "<20":
                total_query += ' AND average_cost_for_two < 20'
            elif average_cost == "20-50":
                total_query += ' AND average_cost_for_two BETWEEN 20 AND 50'
            elif average_cost == "50-500":
                total_query += ' AND average_cost_for_two BETWEEN 50 AND 100'
            elif average_cost == ">1000":
                total_query += ' AND average_cost_for_two > 100'

        if cuisines:
            total_query += ' AND (' + ' OR '.join(['cuisines LIKE ?'] * len(cuisines)) + ')'
            total_params.extend([f'%{cuisine}%' for cuisine in cuisines])

        total_restaurants = conn.execute(total_query, total_params).fetchone()[0]
        total_pages = (total_restaurants + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1

        conn.close()

        if request.path.startswith('/api/'):
            return jsonify({
                'restaurants': [dict(row) for row in restaurants],
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            })

        return render_template(
            'restaurant_list.html',
            restaurants=restaurants,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev,
            search=search,
            ratings=ratings,
            country=country,
            average_cost=average_cost,
            cuisines=cuisines,
            total_pages=total_pages
        )
    except Exception as e:
        app.logger.error(f'Error occurred: {e}')
        if request.path.startswith('/api/'):
            return jsonify({'error': str(e)}), 500
        return render_template('error.html', message=f"An error occurred: {str(e)}"), 500

# Endpoint to get backend details
@app.route('/api/details', methods=['GET'])
def backend_details():
    details = {
        'name': 'Restaurant Listing Backend',
        'version': '1.0',
        'status': 'Running',
        'host': 'localhost',
        'port': 5000
    }
    return jsonify(details)

# New endpoint to display all restaurant data as JSON
@app.route('/api/all-restaurants', methods=['GET'])
def all_restaurants_json():
    try:
        conn = get_db_connection()
        restaurants = conn.execute('SELECT * FROM restaurants').fetchall()
        conn.close()
        return jsonify([dict(row) for row in restaurants])
    except Exception as e:
        app.logger.error(f'Error occurred: {e}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
