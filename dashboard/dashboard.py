import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import textwrap
import zipfile
import io
import plotly.express as px
import requests
from io import BytesIO

# Function to load data
@st.cache_data
def load_data():
    # Define the URL of the GitHub repository where the .zip file is stored
    github_url = "https://github.com/azalliamelani/stackoverflow-2023-survey/raw/main/dashboard/survey_results_public.zip"
    
    # Make a request to download the .zip file
    response = requests.get(github_url)
    
    # Extract the contents of the .zip file
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        # Assume the .zip file contains a single CSV file
        csv_filename = z.namelist()[0]
        with z.open(csv_filename) as f:
            df = pd.read_csv(f)
    
    return df

# Load data
df = load_data()

# Define CSS styles
css_styles = """
<style>
    .element-container:nth-child(1) {
        background-color: #FFCBCB; /* Light blue background for Total Respondents */
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }

    /* Remove the box style for the sidebar image */
    .sidebar .stImage {
        box-shadow: none;
        border-radius: 0;
    }
</style>
"""
# Insert CSS styles into the Streamlit app
st.markdown(css_styles, unsafe_allow_html=True)

# Define CSS styles for the sidebar image
css_styles_sidebar = """
<style>
    .sidebar .stImage img {
        border-radius: 10px; /* Adjust the border-radius as needed */
    }
</style>
"""

# Insert CSS styles for the sidebar image into the Streamlit app
st.markdown(css_styles_sidebar, unsafe_allow_html=True)

# Define a mapping from age ranges to midpoints
age_mapping = {
    'Under 18 years old': 17,
    '18-24 years old': 21,
    '25-34 years old': 29.5,
    '35-44 years old': 39.5,
    '45-54 years old': 49.5,
    '55-64 years old': 59.5,
    '65 years or older': 70
}

# Apply the mapping to create a numeric Age column
df['Age_numeric'] = df['Age'].map(age_mapping)

# Sidebar with logo and filters
st.sidebar.image("https://github.com/azalliamelani/stackoverflow-2023-survey/raw/main/dashboard/logo.png", use_column_width=True)
st.sidebar.title("Filters")

# Respondent type filter
respondent_types = ['All Respondents', 'Professional Developer', 'Learning to Code', 'Other Coders']
respondent_filter = st.sidebar.selectbox("Select Respondent Type", respondent_types)

# Filter data based on respondent type
if respondent_filter == 'Professional Developer':
    filtered_df = df[df['MainBranch'] == 'I am a developer by profession']
elif respondent_filter == 'Learning to Code':
    filtered_df = df[df['MainBranch'] == 'I am learning to code']
elif respondent_filter == 'Other Coders':
    filtered_df = df[~df['MainBranch'].isin(['I am a developer by profession', 'I am learning to code'])]
else:
    filtered_df = df.copy()

# Define other filters
age_filter = st.sidebar.slider("Select Age Range", int(filtered_df['Age_numeric'].min()), int(filtered_df['Age_numeric'].max()), (20, 40))
edlevel_filter = st.sidebar.multiselect("Select Education Level", filtered_df['EdLevel'].unique(), default=filtered_df['EdLevel'].unique())

# Apply filters
filtered_df = filtered_df[
    (filtered_df['Age_numeric'] >= age_filter[0]) & (filtered_df['Age_numeric'] <= age_filter[1]) &
    (filtered_df['EdLevel'].isin(edlevel_filter))
]

# Title of the app
st.title("Stack Overflow 2023 Developer Survey Analysis")

# Demographics Visualizations
st.header("Demographics")

# Metrics for the dashboard
col1, col2, col3 = st.columns(3)

with col1:
    total_respondents = filtered_df.shape[0]
    st.metric("Total Respondents", value=total_respondents)

with col2:
    total_countries = filtered_df['Country'].nunique()
    st.metric("Total Countries", value=total_countries)

with col3:
    avg_age = filtered_df['Age_numeric'].mean()
    st.metric("Average Age", value=f"{avg_age:.1f}")

# Age distribution
st.subheader("Age Distribution :pushpin:")
fig_age = px.histogram(filtered_df, x='Age', nbins=20, title="Age Distribution", color_discrete_sequence=['#FF6969'])
fig_age.update_layout(xaxis_title="Age", yaxis_title="Respondent Count")
st.plotly_chart(fig_age)

# Education level distribution
st.subheader("Education Level Distribution :male-student:")
edu_counts = filtered_df['EdLevel'].value_counts().head(10)  # Get the top 10 education levels by respondent count
fig_edu = px.bar(
    x=edu_counts.values,
    y=edu_counts.index,
    orientation='h',
    labels={'x': 'Respondent Count', 'y': 'Education Level'},
    title='Top 10 Education Levels',
    color_discrete_sequence=['#FF6969']
)
st.plotly_chart(fig_edu)

# Assuming filtered_df is already defined
# Get the top 10 countries by respondent count
st.subheader("Top 10 Respondent Based On Country Distribution :earth_americas:")
top_countries = filtered_df['Country'].value_counts().head(10).reset_index()
top_countries.columns = ['Country', 'Respondent Count']

# Define a custom color scale with shades of pink
custom_color_scale = [
    [0.0, "#FFE5E5"],  # Lightest pink
    [0.2, "#FFC2C2"],
    [0.4, "#FFA0A0"],
    [0.6, "#FF7D7D"],
    [0.8, "#FF5A5A"],
    [1.0, "#FF3737"]   # Darkest pink
]

# Create the choropleth map with the custom color scale
fig_country = px.choropleth(
    top_countries,
    locations="Country",
    locationmode='country names',
    color="Respondent Count",
    color_continuous_scale=custom_color_scale
)
st.plotly_chart(fig_country)

# Add the explanation box
explanation_html = """
<div style="background-color: #FFCBCB; padding: 10px; border-radius: 5px;">
    <h4>Explanation For Each Country</h4>
    <p>1. United States of America: 13,606 Respondents</p>
    <p>2. Germany: 6,052 Respondents</p>
    <p>3. India: 5,097 Respondents</p>
    <p>4. United Kingdom of Great Britain and Northern Ireland: 4,016 Respondents</p>
    <p>5. Canada: 2,686 Respondents</p>
    <p>6. France: 2,496 Respondents</p>
    <p>7. Poland: 2,154 Respondents</p>
    <p>8. Netherlands: 1,914 Respondents</p>
    <p>9. Australia: 2,078 Respondents</p>
    <p>10. Brazil: 1,774 Respondents</p>
</div>
"""
st.markdown(explanation_html, unsafe_allow_html=True)

# Divider
st.markdown("<hr>", unsafe_allow_html=True)

# Programming Experience Visualizations
st.header("Programming Experience :computer:")

# Languages worked with
# Top 10 Most Popular Programming Language Used by Developers
st.subheader("Top 10 Most Popular Programming Languages Used by Developers")
languages_list = filtered_df['LanguageHaveWorkedWith'].str.split(';')
all_languages = [lang for sublist in languages_list.dropna() for lang in sublist]
language_counts = pd.Series(all_languages).value_counts().head(10)

# Create the bar chart with the desired color
fig_lang = px.bar(
    language_counts, 
    y=language_counts.index, 
    x=language_counts.values, 
    orientation='h',
    color_discrete_sequence=['#FF6969'] * len(language_counts)  # Set the color to #69B4FF
)
fig_lang.update_layout(xaxis_title="Respondent Count", yaxis_title="Programming Language")
st.plotly_chart(fig_lang)

# Databases worked with
# Top 10 Most Popular Databases Used by Developers
st.subheader("Top 10 Most Popular Databases Used by Developers")
databases_list = filtered_df['DatabaseHaveWorkedWith'].str.split(';')
all_databases = [db for sublist in databases_list.dropna() for db in sublist]
database_counts = pd.Series(all_databases).value_counts().head(10)

# Create the bar chart with the desired color
fig_db = px.bar(
    database_counts,
    x=database_counts.values,
    y=database_counts.index,
    orientation='h',
    color_discrete_sequence=['#FF6969'] * len(database_counts)  # Set the color to #69B4FF
)
fig_db.update_layout(xaxis_title="Respondent Count", yaxis_title="Database")
st.plotly_chart(fig_db)

# Platforms worked with
# Top 10 Most Popular Cloud Platforms Used by Developers
st.subheader("Top 10 Most Popular Cloud Platforms Used by Developers")
platforms_list = filtered_df['PlatformHaveWorkedWith'].str.split(';')
all_platforms = [platform for sublist in platforms_list.dropna() for platform in sublist]
platform_counts = pd.Series(all_platforms).value_counts().head(10)

# Create the bar chart with the desired color
fig_platform = px.bar(
    platform_counts,
    x=platform_counts.values,
    y=platform_counts.index,
    orientation='h',
    color_discrete_sequence=['#FF6969'] * len(platform_counts)  # Set the color to #69B4FF
)
fig_platform.update_layout(xaxis_title="Respondent Count", yaxis_title="Cloud Platform")
st.plotly_chart(fig_platform)

# Web frameworks worked with
# Top 10 Most Popular Web Frameworks Used by Developers
st.subheader("Top 10 Most Popular Web Frameworks Used by Developers")
webframes_list = filtered_df['WebframeHaveWorkedWith'].str.split(';')
all_webframes = [webframe for sublist in webframes_list.dropna() for webframe in sublist]
webframe_counts = pd.Series(all_webframes).value_counts().head(10)

# Create the bar chart with the desired color
fig_webframe = px.bar(
    webframe_counts,
    x=webframe_counts.values,
    y=webframe_counts.index,
    orientation='h',
    color_discrete_sequence=['#FF6969'] * len(webframe_counts)  # Set the color to #69B4FF
)
fig_webframe.update_layout(xaxis_title="Respondent Count", yaxis_title="Web Framework")
st.plotly_chart(fig_webframe)

# Collaboration tools worked with
# Top 10 Most Popular IDE's Used by Developers
st.subheader("Top 10 Most Popular IDE's Used by Developers")
collabtools_list = filtered_df['NEWCollabToolsHaveWorkedWith'].str.split(';')
all_collabtools = [tool for sublist in collabtools_list.dropna() for tool in sublist]
collabtool_counts = pd.Series(all_collabtools).value_counts().head(10)

# Create the bar chart with the desired color
fig_collabtool = px.bar(
    collabtool_counts,
    x=collabtool_counts.values,
    y=collabtool_counts.index,
    orientation='h',
    color_discrete_sequence=['#FF6969'] * len(collabtool_counts)  # Set the color to #69B4FF
)
fig_collabtool.update_layout(xaxis_title="Respondent Count", yaxis_title="IDE Tools")
st.plotly_chart(fig_collabtool)
