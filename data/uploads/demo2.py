#!/usr/bin/env python
# coding: utf-8

# In[6]:


import folium
from IPython.display import display
import matplotlib.pyplot as plt
import seaborn as sns


# In[7]:


# Sample data for optimized irrigation zones
zones = {
    'Zone': ['A', 'B', 'C'],
    'Latitude': [40.7128, 34.0522, 41.8781],
    'Longitude': [-74.0060, -118.2437, -87.6298],
    'Crop Yield': [80, 65, 90]
}


# In[8]:


# Plotting the map using Folium
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# Add points to the map with popups
for i in range(len(zones['Zone'])):
    folium.Marker(
        location=[zones['Latitude'][i], zones['Longitude'][i]],
        popup=f"Zone: {zones['Zone'][i]}\nCrop Yield: {zones['Crop Yield'][i]}"
    ).add_to(m)

# Display the map in Jupyter Notebook
display(m)


# In[9]:


# Create a more elegant chart using Seaborn
sns.set_theme(style="whitegrid")
plt.figure(figsize=(8, 6))

# Barplot for crop yield
sns.barplot(x=zones['Zone'], y=zones['Crop Yield'], palette="viridis")

# Add labels and title
plt.xlabel('Irrigation Zone', fontsize=12)
plt.ylabel('Crop Yield', fontsize=12)
plt.title('Crop Yield in Optimized Irrigation Zones', fontsize=14)

# Show the plot
plt.show()


# In[10]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap


# In[12]:


# Simulated data for a single random field in Catalonia
data = {
    'Field': ['Field_1'] * 100,
    'Latitude': [41.3851 + 0.01 * i for i in range(100)],  # Random latitude values around Barcelona
    'Longitude': [2.1734 + 0.01 * i for i in range(100)],  # Random longitude values around Barcelona
    'Yield': [round(50 + (i % 10) * 5 + (i % 3) * 2, 2) for i in range(100)],  # Simulated yield values
    'Soil_Moisture': [round(20 + (i % 5) * 3, 2) for i in range(100)],        # Simulated soil moisture
    'Rainfall': [round(30 + (i % 7) * 4, 2) for i in range(100)]             # Simulated rainfall
}

df = pd.DataFrame(data)


# In[13]:


# --- Visualization 1: Yield Distribution ---
sns.set_theme(style="whitegrid")
plt.figure(figsize=(8, 6))
sns.histplot(df['Yield'], kde=True, color='blue', bins=15)
plt.title('Yield Distribution for Field_1', fontsize=16)
plt.xlabel('Yield (tons/ha)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.show()


# In[14]:


# --- Visualization 2: Correlation Heatmap ---
plt.figure(figsize=(8, 6))
correlation = df[['Yield', 'Soil_Moisture', 'Rainfall']].corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Between Variables', fontsize=16)
plt.show()


# In[15]:


# --- Visualization 3: Yield vs Soil Moisture ---
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='Soil_Moisture', y='Yield', hue='Rainfall', palette='viridis', size='Rainfall')
plt.title('Yield vs Soil Moisture (Colored by Rainfall)', fontsize=16)
plt.xlabel('Soil Moisture (%)', fontsize=12)
plt.ylabel('Yield (tons/ha)', fontsize=12)
plt.legend(title='Rainfall (mm)', loc='upper left')
plt.show()


# In[18]:


# --- Visualization 4: Interactive Map with Yield Density ---
m = folium.Map(location=[41.3851, 2.1734], zoom_start=10)  # Centered on Barcelona

# Prepare data for heatmap
heat_data = [[row['Latitude'], row['Longitude'], row['Yield']] for index, row in df.iterrows()]

# Add heatmap layer to the map
HeatMap(heat_data).add_to(m)

# Save and display the map (for Jupyter Notebook users)
m.save("yield_density_map.html")
print("Interactive map saved as 'yield_density_map.html'. Open it to view the map.")


# In[19]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap

# Simulated data for a single random field in Catalonia
data = {
    'Date': pd.date_range(start="2025-01-01", periods=100, freq='D'),  # Simulated dates
    'Latitude': [41.3851 + 0.01 * i for i in range(100)],  # Random latitude values around Barcelona
    'Longitude': [2.1734 + 0.01 * i for i in range(100)],  # Random longitude values around Barcelona
    'Yield': [round(50 + (i % 10) * 5 + (i % 3) * 2, 2) for i in range(100)],  # Simulated yield values
    'Soil_Moisture': [round(20 + (i % 5) * 3, 2) for i in range(100)],        # Simulated soil moisture
}

df = pd.DataFrame(data)

# --- Visualization 1: Yield Variability Over Time ---
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Date', y='Yield', color='green', linewidth=2)
plt.title('Crop Yield Variability Over Time', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Yield (tons/ha)', fontsize=12)
plt.xticks(rotation=45)
plt.show()

# --- Visualization 2: Water Stress vs Yield ---
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='Soil_Moisture', y='Yield', color='blue', s=50)
plt.title('Water Stress (Soil Moisture) vs Crop Yield', fontsize=16)
plt.xlabel('Soil Moisture (%)', fontsize=12)
plt.ylabel('Crop Yield (tons/ha)', fontsize=12)
plt.show()

# --- Visualization 3: Interactive Map with Yield Density ---
m = folium.Map(location=[41.3851, 2.1734], zoom_start=10)  # Centered on Barcelona

# Prepare data for heatmap
heat_data = [[row['Latitude'], row['Longitude'], row['Yield']] for index, row in df.iterrows()]

# Add heatmap layer to the map
HeatMap(heat_data).add_to(m)

# Display the map directly in Jupyter Notebook or interactive environments
from IPython.display import display
display(m)


# In[20]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster


# In[21]:


# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Generate synthetic data for demonstration
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", end="2023-07-31", freq='W')
data = {
    'Date': dates,
    'Soil Moisture (%)': np.random.normal(20, 5, len(dates)).clip(10, 30),
    'Predicted Yield (kg/ha)': np.linspace(80, 150, len(dates)) + np.random.normal(0, 10, len(dates)),
    'Water Stress Level': np.random.choice(['Low', 'Medium', 'High'], len(dates), p=[0.2, 0.5, 0.3]),
    'Irrigation Zone': np.random.choice(['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E'], len(dates))
}

df = pd.DataFrame(data)


# In[23]:


# Visualization 1: Time Series of Soil Moisture and Yield
plt.figure(figsize=(14, 6))
ax1 = sns.lineplot(x='Date', y='Soil Moisture (%)', data=df, color='#1f77b4', label='Soil Moisture')
ax2 = plt.twinx()
sns.lineplot(x='Date', y='Predicted Yield (kg/ha)', data=df, color='#ff7f0e', ax=ax2, label='Predicted Yield')
plt.title('Soil Moisture and Predicted Yield Over Time', fontsize=16, pad=20)
ax1.figure.legend(loc='upper right', bbox_to_anchor=(0.85, 0.9))
plt.tight_layout()
plt.savefig('time_series.png')
plt.close()

# Visualization 2: Water Stress Impact by Irrigation Zone
plt.figure()
ax = sns.barplot(x='Irrigation Zone', y='Predicted Yield (kg/ha)', 
                hue='Water Stress Level', data=df, palette='YlOrRd_r',
                order=['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E'])
plt.title('Yield Distribution by Irrigation Zone and Water Stress Level', fontsize=14)
plt.legend(title='Water Stress', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('barplot.png')
plt.close()

# Visualization 3: Yield vs. Soil Moisture Relationship
plt.figure()
scatter = sns.regplot(x='Soil Moisture (%)', y='Predicted Yield (kg/ha)', data=df,
                     scatter_kws={'alpha':0.6, 'color':'#2ca02c'},
                     line_kws={'color':'#d62728'})
plt.title('Yield Relationship with Soil Moisture Content', fontsize=14)
plt.tight_layout()
plt.savefig('scatterplot.png')
plt.close()

# Visualization 4: Interactive Yield Density Map (Folium)
# Generate synthetic coordinates for a field in Catalonia (near Lleida)
lat_points = 41.6167 + np.random.normal(0, 0.01, 100)
lon_points = 0.6167 + np.random.normal(0, 0.01, 100)
yield_density = np.random.uniform(50, 150, 100)

# Create base map
m = folium.Map(location=[41.6167, 0.6167], zoom_start=14, tiles='cartodbpositron')

# Add marker cluster
marker_cluster = MarkerCluster().add_to(m)

# Add points with yield information
for lat, lon, yld in zip(lat_points, lon_points, yield_density):
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color='#3186cc' if yld > 100 else '#e6550d',
        fill=True,
        fill_opacity=0.7,
        popup=f'Yield: {yld:.1f} kg/ha'
    ).add_to(m)

# Add heatmap layer for density visualization
from folium.plugins import HeatMap
heat_data = [[lat, lon, yld] for lat, lon, yld in zip(lat_points, lon_points, yield_density)]
HeatMap(heat_data, radius=15).add_to(m)

# Save map
m.save('yield_density_map.html')


# In[25]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster, HeatMap
from IPython.display import display


# In[26]:


# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 100

# Generate synthetic data
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", end="2023-07-31", freq='W')
data = {
    'Date': dates,
    'Soil Moisture (%)': np.random.normal(20, 5, len(dates)).clip(10, 30),
    'Predicted Yield (kg/ha)': np.linspace(80, 150, len(dates)) + np.random.normal(0, 10, len(dates)),
    'Water Stress Level': np.random.choice(['Low', 'Medium', 'High'], len(dates), p=[0.2, 0.5, 0.3]),
    'Irrigation Zone': np.random.choice(['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E'], len(dates))
}
df = pd.DataFrame(data)


# In[28]:


# 1. Time Series Visualization
fig1, ax1 = plt.subplots()
sns.lineplot(x='Date', y='Soil Moisture (%)', data=df, color='#1f77b4', ax=ax1)
ax2 = ax1.twinx()
sns.lineplot(x='Date', y='Predicted Yield (kg/ha)', data=df, color='#ff7f0e', ax=ax2)
ax1.set_title('Soil Moisture vs Predicted Yield Over Time', fontsize=14, pad=20)
fig1.legend(labels=['Soil Moisture', 'Predicted Yield'], 
           loc='upper right', bbox_to_anchor=(0.85, 0.9))
plt.tight_layout()
plt.show()


# In[29]:


# 2. Water Stress Impact Visualization
plt.figure()
ax = sns.barplot(x='Irrigation Zone', y='Predicted Yield (kg/ha)', 
                hue='Water Stress Level', data=df, palette='YlOrRd_r',
                order=['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E'])
plt.title('Yield Distribution by Irrigation Zone and Water Stress', fontsize=14)
plt.legend(title='Water Stress', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[30]:


# 3. Yield vs Soil Moisture Relationship
plt.figure()
scatter = sns.regplot(x='Soil Moisture (%)', y='Predicted Yield (kg/ha)', data=df,
                     scatter_kws={'alpha':0.6, 'color':'#2ca02c'},
                     line_kws={'color':'#d62728'})
plt.title('Yield Relationship with Soil Moisture Content', fontsize=14)
plt.tight_layout()
plt.show()


# In[31]:


# 4. Interactive Yield Density Map
# Generate synthetic coordinates (near Lleida, Catalonia)
lat_points = 41.6167 + np.random.normal(0, 0.01, 100)
lon_points = 0.6167 + np.random.normal(0, 0.01, 100)
yield_density = np.random.uniform(50, 150, 100)

# Create interactive map
m = folium.Map(location=[41.6167, 0.6167], zoom_start=14, tiles='cartodbpositron')
marker_cluster = MarkerCluster().add_to(m)

# Add yield markers
for lat, lon, yld in zip(lat_points, lon_points, yield_density):
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color='#3186cc' if yld > 100 else '#e6550d',
        fill=True,
        fill_opacity=0.7,
        popup=f'Yield: {yld:.1f} kg/ha'
    ).add_to(marker_cluster)

# Add heatmap
HeatMap([[lat, lon, yld] for lat, lon, yld in zip(lat_points, lon_points, yield_density)], 
        radius=15).add_to(m)

# Display map inline
display(m)


# In[38]:


import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster, HeatMap
from IPython.display import display

# Install required packages if needed
# !pip install plotly folium pandas numpy


# In[39]:


# Generate synthetic data
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", end="2023-07-31", freq='W')
data = {
    'Date': dates,
    'Soil Moisture (%)': np.random.normal(20, 5, len(dates)).clip(10, 30),
    'Predicted Yield (kg/ha)': np.linspace(80, 150, len(dates)) + np.random.normal(0, 10, len(dates)),
    'Water Stress Level': np.random.choice(['Low', 'Medium', 'High'], len(dates), p=[0.2, 0.5, 0.3]),
    'Irrigation Zone': np.random.choice(['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E'], len(dates))
}
df = pd.DataFrame(data)


# In[52]:


# 1. Interactive Time Series with Range Selector (Plotly)
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Soil Moisture (%)'],
    name='Soil Moisture',
    line=dict(color='#1f77b4'),
    yaxis='y1'
))

fig1.add_trace(go.Scatter(
    x=df['Date'],
    y=df['Predicted Yield (kg/ha)'],
    name='Predicted Yield',
    line=dict(color='#ff7f0e'),
    yaxis='y2'
))

fig1.update_layout(
    title='Interactive Soil Moisture & Yield Timeline',
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    ),
    yaxis=dict(title='Soil Moisture (%)', color='#1f77b4'),
    yaxis2=dict(
        title='Predicted Yield (kg/ha)',
        color='#ff7f0e',
        overlaying='y',
        side='right'
    ),
    hovermode="x unified"
)
fig1.show()


# In[53]:


# 2. Corrected Interactive Yield Distribution Visualization
# Preprocess data
agg_df = df.groupby(['Irrigation Zone', 'Water Stress Level'])['Predicted Yield (kg/ha)'].mean().reset_index()

# Create initial figure
fig2 = px.bar(agg_df,
             x='Irrigation Zone',
             y='Predicted Yield (kg/ha)',
             color='Water Stress Level',
             barmode='group',
             color_discrete_sequence=px.colors.sequential.OrRd[::-1],
             category_orders={
                 "Water Stress Level": ["Low", "Medium", "High"],
                 "Irrigation Zone": ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E"]
             },
             title='Yield Distribution by Zone and Stress Level')

# Create dropdown buttons
zone_options = [{'label': 'All Zones', 'value': 'All'}]
zone_options += [{'label': zone, 'value': zone} for zone in df['Irrigation Zone'].unique()]

buttons = [dict(label='All Zones',
               method='update',
               args=[{'visible': [True]*len(agg_df)},
                     {'title': 'All Zones'}])]

for zone in df['Irrigation Zone'].unique():
    buttons.append(
        dict(label=zone,
             method='update',
             args=[{'visible': [(agg_df['Irrigation Zone'] == zone).values]},
                   {'title': f'Zone {zone[-1]}'}])
)

fig2.update_layout(
    updatemenus=[dict(
        type='dropdown',
        showactive=True,
        buttons=buttons,
        x=0.1,
        xanchor='left',
        y=1.15,
        yanchor='top'
    )]
)

# Add unified legend and proper spacing
fig2.update_layout(
    legend_title_text='Water Stress',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=100)
)

fig2.show()


# In[54]:


# 3. Interactive Yield vs Moisture Scatter Plot (Plotly)
fig3 = px.scatter(df,
                 x='Soil Moisture (%)',
                 y='Predicted Yield (kg/ha)',
                 color='Water Stress Level',
                 trendline="lowess",
                 hover_data=['Date', 'Irrigation Zone'],
                 color_discrete_map={
                     'Low': '#2ca02c',
                     'Medium': '#ff7f0e',
                     'High': '#d62728'
                 },
                 title='Interactive Yield-Moisture Relationship')

fig3.update_traces(marker=dict(size=12, opacity=0.7))
fig3.update_layout(
    hovermode='closest',
    xaxis=dict(range=[10, 30]),
    yaxis=dict(range=[50, 200])
)
fig3.show()


# In[55]:


# 4. Enhanced Interactive Yield Map with proper rendering
from IPython.display import HTML, display

# Generate coordinates
lat_points = 41.6167 + np.random.normal(0, 0.01, 100)  # Near Lleida, Catalonia
lon_points = 0.6167 + np.random.normal(0, 0.01, 100)
yield_density = np.random.uniform(50, 150, 100)

# Create base map
m = folium.Map(location=[41.6167, 0.6167], zoom_start=14, tiles='cartodbpositron')

# Add HTML titles directly to the map
m.get_root().html.add_child(folium.Element('''
    <h3 style="position:fixed; top:10px; left:50px; z-index:1000; 
    background-color:rgba(255,255,255,0.8); padding:10px; border-radius:5px;
    font-family:Arial; font-size:16px">
    Field Yield Analysis<br>
    <span style="font-size:12px; color:#666">Lleida, Catalonia | 2023 Season</span>
    </h3>
'''))

# Add markers
marker_cluster = MarkerCluster(name="Yield Points").add_to(m)
for lat, lon, yld in zip(lat_points, lon_points, yield_density):
    folium.CircleMarker(
        location=[lat, lon],
        radius=6,
        color='#3186cc' if yld > 100 else '#e6550d',
        fill=True,
        fill_opacity=0.7,
        popup=f'Yield: {yld:.1f} kg/ha',
        tooltip="Click for details"
    ).add_to(marker_cluster)

# Add heatmap
HeatMap([[lat, lon, yld] for lat, lon, yld in zip(lat_points, lon_points, yield_density)], 
        radius=15, name="Yield Density").add_to(m)

# Add layer control
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Display in notebook
display(HTML(m._repr_html_()))


# In[ ]:




