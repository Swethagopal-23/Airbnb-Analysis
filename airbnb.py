import streamlit as st
import pandas as pd
import plotly.express as px 
import pymysql
import base64   

# Function to add a local image as background
def set_bg_image(image_file):
    with open(image_file, "rb") as image:
        encoded_string = base64.b64encode(image.read()).decode()
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    h1 {{
        color: #ff4c4c; /* Change this to your desired font color for the title */
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Call the function with your image path
set_bg_image("bg.webp") 
                                   
# Function to create a MySQL connection
def create_connection(user, password, host, database):
    connection = pymysql.connect(user=user, password=password, host=host, database=database)
    return connection    

# Database credentials
user = 'root'
password = '12345678'
host = 'localhost'  
database = 'airbnb'

# Create a connection to the database
conn = create_connection(user, password, host, database)

# Function to load data from MySQL
def load_data(table_name):
    query = f"SELECT * FROM {table_name};"
    return pd.read_sql(query, conn)

# Load data from MySQL database
hotels_df = load_data('hotels')
price_df = load_data('pricing')
hosts_df = load_data('hosts')
availability_df = load_data('availability')
property_df = load_data('properties')
review_scores_df = load_data('review_scores')
review_df = load_data('reviews')

# Merge 'hotels_df' with 'price_df' to include 'price' column
hotels_df = hotels_df.copy()
hotels_df['price'] = price_df['price']

# Split 'coordinates' into 'latitude' and 'longitude'
hotels_df[['longitude', 'latitude']] = hotels_df['coordinates'].str.split(', ', expand=True)
hotels_df['latitude'] = hotels_df['latitude'].astype(float)
hotels_df['longitude'] = hotels_df['longitude'].astype(float)

# Streamlit App Layout
st.title("AIRBNB ANALYSIS")

# Home Tab (optional)
tab_home, tab1, tab2, tab3, tab4 = st.tabs(["Home", "Map Visualization", "Price Analysis", "Property Analysis", "Review Analysis"])

with tab_home:
  
    st.subheader("Welcome to the Airbnb Analysis Dashboard")
    st.subheader("Explore Listings, Prices, Properties, and Reviews")
    
    st.write("""
        This dashboard allows you to explore Airbnb listings data through various interactive visualizations.
        You can navigate through the different tabs for in-depth analyses on prices, property types, availability, and guest reviews. 
        Here's a brief overview of the features:
        - **Map Visualization**: View properties on an interactive map based on location and price.
        - **Price Analysis**: Explore price distributions and comparisons.
        - **Property Analysis**: Dive into property details such as room types, bed types, and amenities.
        - **Review Analysis**: Examine guest review scores for cleanliness, communication, and overall satisfaction.
    """)
    
# Map Visualization Tab     
with tab1:
    st.header("Property Map - Prices by Location")

    selected_country = st.selectbox('Select Country', hotels_df['country'].unique(), key='country_select')

    # Filter streets based on the selected country
    streets_in_country = hotels_df[hotels_df['country'] == selected_country]['street'].unique()
    selected_street = st.selectbox('Select Street', streets_in_country, key='street_select')

    filtered_hotels = hotels_df[(hotels_df['country'] == selected_country) & (hotels_df['street'] == selected_street)]

    filtered_hotels = filtered_hotels.dropna(subset=['price'])

    filtered_hotels[['longitude', 'latitude']] = filtered_hotels['coordinates'].str.split(', ', expand=True)
    filtered_hotels['latitude'] = filtered_hotels['latitude'].astype(float)
    filtered_hotels['longitude'] = filtered_hotels['longitude'].astype(float)

    filtered_hotels['price'] = pd.to_numeric(filtered_hotels['price'], errors='coerce')

    fig_map = px.scatter_mapbox(filtered_hotels, 
                                lat='latitude', 
                                lon='longitude', 
                                hover_name='name', 
                                hover_data=['price'], 
                                color='price', 
                                size='price', 
                                zoom=10, 
                                mapbox_style="open-street-map")

    st.plotly_chart(fig_map)

# Price Analysis Tab
with tab2:
    st.header("Price Analysis Dashboard")

    analysis_type = st.selectbox("Select Price Distribution Analysis",
                                  ["Box Plot for Price Distribution",
                                   "Comparison of Price Types",
                                   "Distribution of Prices by Cancellation Policy",
                                   "Interactive Scatter Plot"])

    if analysis_type == "Box Plot for Price Distribution":
        fig_box = px.box(price_df, 
                         y=['price', 'weekly_price', 'monthly_price'],
                         title="Price Distribution Analysis")
        st.plotly_chart(fig_box)    

    elif analysis_type == "Comparison of Price Types":
        avg_prices = price_df[['price', 'weekly_price', 'monthly_price']].mean().reset_index()
        avg_prices.columns = ['Price Type', 'Average Price']

        fig_bar = px.bar(avg_prices, 
                         x='Price Type', 
                         y='Average Price', 
                         title="Average Price Comparison")
        st.plotly_chart(fig_bar)

    elif analysis_type == "Distribution of Prices by Cancellation Policy":
        fig_violin = px.violin(price_df, 
                               y='price', 
                               x='cancellation_policy', 
                               box=True, 
                               title="Price Distribution by Cancellation Policy")
        st.plotly_chart(fig_violin)

    elif analysis_type == "Interactive Scatter Plot":
        fig_scatter = px.scatter(price_df, 
                                  x='cleaning_fee', 
                                  y='price', 
                                  title="Price vs Cleaning Fee",
                                  hover_data=['security_deposit'])
        st.plotly_chart(fig_scatter)

# Properties Analysis Tab
with tab3:
    st.header("Properties Analysis")

    visualization_options = [
        "Property Type Distribution",
        "Room Type Distribution",
        "Bed Type Distribution",
        "Amenities Frequency",
        "Accommodates Distribution"
    ]
    selected_visualization = st.selectbox("Select Visualization Type", visualization_options)

    if selected_visualization == "Property Type Distribution":
        st.subheader("Property Type Distribution")
        property_counts = property_df['property_type'].value_counts().reset_index()
        property_counts.columns = ['property_type', 'count']
        fig_property_type = px.pie(property_counts, 
                                    names='property_type', 
                                    values='count', 
                                    title="Property Type Distribution")
        st.plotly_chart(fig_property_type)

    elif selected_visualization == "Room Type Distribution":
        st.subheader("Room Type Distribution")
        room_counts = property_df['room_type'].value_counts().reset_index()
        room_counts.columns = ['room_type', 'count']
        fig_room_type = px.pie(room_counts, 
                                names='room_type', 
                                values='count', 
                                title="Room Type Distribution")
        st.plotly_chart(fig_room_type)

    elif selected_visualization == "Bed Type Distribution":
        st.subheader("Bed Type Distribution")
        bed_counts = property_df['bed_type'].value_counts().reset_index()
        bed_counts.columns = ['bed_type', 'count']
        fig_bed_type = px.bar(bed_counts, 
                              x='count', 
                              y='bed_type', 
                              orientation='h',
                              title="Bed Type Distribution")
        st.plotly_chart(fig_bed_type)

    elif selected_visualization == "Amenities Frequency":
        st.subheader("Frequency of Amenities")
        amenities_counts = property_df['amenities'].str.get_dummies(sep=', ').sum().reset_index()
        amenities_counts.columns = ['amenity', 'count']
        fig_amenities = px.bar(amenities_counts, 
                                x='count', 
                                y='amenity', 
                                orientation='h', 
                                title="Frequency of Amenities")
        st.plotly_chart(fig_amenities)

    elif selected_visualization == "Accommodates Distribution":
        st.subheader("Accommodates Distribution")
        fig_accommodates = px.histogram(property_df, 
                                         x='accommodates', 
                                         title="Distribution of Accommodates")
        st.plotly_chart(fig_accommodates)

# Review Analysis Tab
with tab4:
    st.header("Review Analysis")

    visualization_options = [
        "Cleanliness Score Distribution", 
        "Check-in Score Distribution", 
        "Location Score Distribution", 
        "Communication Score Distribution", 
        "Overall Score Distribution",
        "Average Scores Overview"
    ]
    selected_visualization = st.selectbox("Select Visualization Type", visualization_options)

    if selected_visualization == "Cleanliness Score Distribution":
        st.subheader("Cleanliness Score Distribution")
        fig_cleanliness = px.histogram(review_scores_df, 
                                        x='cleanliness_score', 
                                        title="Distribution of Cleanliness Scores", 
                                        nbins=5)
        st.plotly_chart(fig_cleanliness)

    elif selected_visualization == "Check-in Score Distribution":
        st.subheader("Check-in Score Distribution")
        fig_checkin = px.box(review_scores_df, 
                              y='checkin_score', 
                              title="Check-in Score Distribution")
        st.plotly_chart(fig_checkin)

    elif selected_visualization == "Location Score Distribution":
        st.subheader("Location Score Distribution")
        fig_location = px.violin(review_scores_df, 
                                 y='location_score', 
                                 title="Location Score Distribution")
        st.plotly_chart(fig_location)

    elif selected_visualization == "Communication Score Distribution":
        st.subheader("Communication Score Distribution")
        fig_communication = px.scatter(review_scores_df, 
                                        x='communication_score', 
                                        y='overall_score', 
                                        title="Communication Score vs Overall Score", 
                                        trendline="ols")
        st.plotly_chart(fig_communication)

    elif selected_visualization == "Overall Score Distribution":
        st.subheader("Overall Score Distribution")
        fig_overall = px.bar(review_scores_df, 
                              x='overall_score', 
                              title="Overall Score Distribution", 
                              color='overall_score')
        st.plotly_chart(fig_overall)

    elif selected_visualization == "Average Scores Overview":
        st.subheader("Average Scores Overview")
        avg_scores = review_scores_df[['cleanliness_score', 'checkin_score', 'location_score', 
                                        'communication_score', 'overall_score']].mean().reset_index()
        avg_scores.columns = ['Score Type', 'Average Score']
        fig_avg_scores = px.bar(avg_scores, 
                                 x='Score Type', 
                                 y='Average Score', 
                                 title="Average Scores Overview")
        st.plotly_chart(fig_avg_scores)


