from flask import Flask, render_template, request
import pandas as pd
import networkx as nx
from datetime import datetime

app = Flask(__name__)

file_path = "data/updated_traffic_data.csv"
traffic_data = pd.read_csv(file_path)

def classify_traffic(count):
    if count < 2:
        return 'Loose'
    elif 2 <= count < 5:
        return 'Moderate'
    else:
        return 'Congested'

G = nx.Graph()

for index, row in traffic_data.iterrows():
    location = row['Location']
    congestion_level = row['Congestion_Level']
    time = row['Time']
    

    if index < len(traffic_data) - 1:
        next_location = traffic_data.iloc[index + 1]['Location']
        G.add_edge(location, next_location, weight=congestion_level)
        G.add_edge(next_location, location, weight=congestion_level)  


def find_best_route(start_location, end_location):
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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_route', methods=['POST'])
def get_route():
    start_location = request.form['start']
    end_location = request.form['end']
    current_time = request.form['time']
    

    current_time = datetime.strptime(current_time, '%H:%M')
    
 
    best_route, error = find_best_route(start_location, end_location)
    
    if error:
       
        return render_template('error.html', error_message=error)
    
   
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
