import plotly.express as px
import pandas as pd

def plot_coordinates(coordinates, labels=None, color_groups=None, 
                    map_style="open-street-map", zoom=10, title="Coordinate Plot"):
    """
    Plot longitude/latitude coordinates on an interactive map with customizable colors.
    
    Parameters:
    - coordinates: List of tuples/lists in (Longitude, Latitude) format
    - labels: Optional list of labels for each point
    - color_groups: List specifying color group for each point (e.g., [0,0,1,1,0])
    - map_style: Map style (default: "open-street-map")
    - zoom: Initial zoom level (default: 10)
    - title: Plot title (default: "Coordinate Plot")
    """
    # Create DataFrame
    df = pd.DataFrame(coordinates, columns=['Longitude', 'Latitude'])
    
    # Add labels if provided
    if labels and len(labels) == len(coordinates):
        df['Label'] = labels
    
    # Add color groups if provided
    if color_groups and len(color_groups) == len(coordinates):
        df['ColorGroup'] = color_groups
        color_discrete_map = {0: 'blue', 1: 'red', 2: 'purple'}  # Customize your colors here
    else:
        print("Single color")
        df['ColorGroup'] = 0  # Default single color
        color_discrete_map = {0: 'blue'}
    
    # Create the map
    fig = px.scatter_mapbox(df,
                          lon="Longitude",
                          lat="Latitude",
                          hover_name="Label" if 'Label' in df.columns else None,
                          color='ColorGroup',
                          color_discrete_map=color_discrete_map,
                          zoom=zoom,
                          height=600,
                          width=800,
                          title=title)
    
    # Configure map
    fig.update_layout(mapbox_style=map_style)
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    
    return fig

# Example usage
if __name__ == "__main__":
    coordinates = [
        (-113.61880757370292, 53.43914566079182),
        (-113.5678950301022, 53.462328050963656),  # A
        (-113.59709132268893, 53.47578144319133),   # B
        (-113.56411479387198, 53.474919787885014),  # C
        (-113.52566898659877, 53.51664209748684)
    ]
    
    labels = ["Point 1", "A", "B", "C", "Point 5"]
    color_groups = [0, 1, 1, 0, 1]  # 0=blue, 1=red
    
    fig = plot_coordinates(coordinates,
                         labels=labels,
                         color_groups=color_groups,
                         map_style="stamen-terrain",
                         zoom=11,
                         title="Edmonton Locations with Color Coding")
    
    fig.show()