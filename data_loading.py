import sqlite3
import pandas as pd

# Load the data
data = pd.read_csv('./zomato.csv', encoding='latin1')  # or 'iso-8859-1' or 'cp1252'

# Rename columns to match your database schema
data = data.rename(columns={
    'Restaurant ID': 'id',
    'Restaurant Name': 'name',
    'Country Code': 'country',
    'City': 'city',
    'Address': 'address',
    'Locality': 'locality',
    'Locality Verbose': 'locality_verbose',
    'Longitude': 'longitude',
    'Latitude': 'latitude',
    'Cuisines': 'cuisines',
    'Average Cost for two': 'average_cost_for_two',
    'Currency': 'currency',
    'Has Table booking': 'has_table_booking',
    'Has Online delivery': 'has_online_delivery',
    'Is delivering now': 'is_delivering_now',
    'Switch to order menu': 'switch_to_order_menu',
    'Price range': 'price_range',
    'Aggregate rating': 'aggregate_rating',
    'Rating color': 'rating_color',
    'Rating text': 'rating_text',
    'Votes': 'votes'
})

# Ensure boolean fields are converted correctly
data['has_table_booking'] = data['has_table_booking'].apply(lambda x: x == 'Yes')
data['has_online_delivery'] = data['has_online_delivery'].apply(lambda x: x == 'Yes')
data['is_delivering_now'] = data['is_delivering_now'].apply(lambda x: x == 'Yes')
data['switch_to_order_menu'] = data['switch_to_order_menu'].apply(lambda x: x == 'Yes')

# Connect to SQLite database
conn = sqlite3.connect('zomato.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY,
        name TEXT,
        country INTEGER,
        city TEXT,
        address TEXT,
        locality TEXT,
        locality_verbose TEXT,
        longitude REAL,
        latitude REAL,
        cuisines TEXT,
        average_cost_for_two INTEGER,
        currency TEXT,
        has_table_booking BOOLEAN,
        has_online_delivery BOOLEAN,
        is_delivering_now BOOLEAN,
        switch_to_order_menu BOOLEAN,
        price_range INTEGER,
        aggregate_rating REAL,
        rating_color TEXT,
        rating_text TEXT,
        votes INTEGER
    )
''')

# Insert data into table
data.to_sql('restaurants', conn, if_exists='replace', index=False)

conn.commit()
conn.close()
