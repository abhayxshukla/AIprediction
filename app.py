from flask import Flask, render_template, request
import pandas as pd
import networkx as nx
from datetime import datetime

app = Flask(__name__)

# Reading the traffic data from CSV file 
file_path = "data/updated_traffic_data.csv"
traffic_data = pd.read_csv(file_path)

# Function to classify traffic based on count
def classify_traffic(count):
    if count < 2:
        return 'Loose'
    elif 2 <= count < 5:
        return 'Moderate'
    else:
        return 'Congested'

# Creating an undirected graph to allow bidirectional travel between intersections
G = nx.Graph()

# Adding edges to the graph based on congestion levels and time
for index, row in traffic_data.iterrows():
    location = row['Location']
    congestion_level = row['Congestion_Level']
    time = row['Time']  # Time from the CSV file
    
    # Assuming each row provides information about transitions to the next intersection
    if index < len(traffic_data) - 1:
        next_location = traffic_data.iloc[index + 1]['Location']
        # Add both directions to the graph for bidirectional travel
        G.add_edge(location, next_location, weight=congestion_level)
        G.add_edge(next_location, location, weight=congestion_level)  # Add reverse edge

# Simplified route suggestion based on congestion
def find_best_route(start_location, end_location):
    # Check if the locations exist in the graph
    if start_location not in G:
        print(f"Error: Start location {start_location} does not exist in the graph.")
        return None, "The start location does not exist in the traffic data."
    if end_location not in G:
        print(f"Error: End location {end_location} does not exist in the graph.")
        return None, "The end location does not exist in the traffic data."

    try:
        best_route = nx.shortest_path(G, start_location, end_location, weight='weight')
        return best_route, None
    except nx.NetworkXNoPath:
        print(f"No path available between {start_location} and {end_location}.")
        return None, "No path available between these locations."

# Home route to render the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to process form data and display results
@app.route('/get_route', methods=['POST'])
def get_route():
    start_location = request.form['start']
    end_location = request.form['end']
    current_time = request.form['time']
    
    # Converting user input to datetime object for comparison
    current_time = datetime.strptime(current_time, '%H:%M')
    
    # Finding the best route based on congestion levels
    best_route, error = find_best_route(start_location, end_location)
    
    if error:
        # Displaying error message if there’s an issue with the locations or no path
        return render_template('error.html', error_message=error)
    
    # Get traffic statuses on the best route
    traffic_status = []
    for location in best_route:
        congestion_level = traffic_data.loc[traffic_data['Location'] == location, 'Congestion_Level'].values[0]
        time_at_location = traffic_data.loc[traffic_data['Location'] == location, 'Time'].values[0]
        
        traffic_status.append({
            'location': location,
            'congestion': classify_traffic(congestion_level),
            'time': time_at_location
        })
    
    return render_template('result.html', best_route=best_route, traffic_status=traffic_status)

if __name__ == '__main__':
    app.run(debug=True)
