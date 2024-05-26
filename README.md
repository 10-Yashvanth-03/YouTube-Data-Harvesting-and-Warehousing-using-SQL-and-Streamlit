# YouTube Data Harvesting and Warehousing using SQL and Streamlit

## Project Overview

This project involves harvesting YouTube data using the YouTube Data API, storing it in a MySQL database, and visualizing the data using a Streamlit dashboard. The aim is to facilitate data analysis and insights through efficient data collection, storage, and visualization.
## Domain
- Social Media

## Skills take away 
- Python scripting 
- Data Collection 
- Streamlit 
- API integration 
- Data Management using SQL  


## Features

- **Data Harvesting**: Collects data from YouTube channels, videos, and comments.
- **Data Warehousing**: Stores the collected data in a MySQL database.
- **Data Visualization**: Interactive Streamlit dashboard for analyzing the data.

## Installation

- Visual Studio
- Jupyter Notebook
- Python (latest version)
- MySql
- Youtube API KEY

## Import Libraries

#### Youtube API libraries
- import googleapiclient.discovery
- from googleapiclient.errors import HttpError

#### Dash board libraries
- import streamlit as st
- rom streamlit_option_menu import option_menu

#### pandas
- import pandas as pd

#### SQL libraries
- import mysql.connector
- from sqlalchemy import create_engine

#### File handling libraries
- import json

#### formatting ISO 8601 date and duration
- import isodate

#### 'timedelta' represents a duration of time
- from datetime import timedelta

#### Python Imaging Library (PIL) adds image
- from PIL import Image

#### manipulating dates and times
- from datetime import datetime

## Approach

#### 1.Identify Data Requirements:
- Here we need Data from YouTube, such as channel information, video details, and comments.

#### 2.YouTube Data API Integration:
- Utilize the YouTube Data API to programmatically access and retrieve data from YouTube.
- Set up API authentication and obtain necessary credentials (API key).

#### 3.Data Harvesting Script:
- Develop a Python script to interact with the YouTube Data API and retrieve desired data.
- Implement functions to collect data for channels, videos, and comments based on predefined criteria.

#### 4.Data Cleaning and Preprocessing:
- Process the retrieved data to clean and preprocess it as necessary.

#### 5.MySQL Database Setup:
- Set up a MySQL database to store the harvested YouTube data.
- Design an appropriate database schema to accommodate different types of data (channels, videos, comments).
- Create tables with suitable column definitions and relationships to represent the data accurately.

#### 6.Data Loading and Warehousing:
- Develop Python scripts or use database management tools to load the cleaned data into the MySQL database.
- Implement data warehousing techniques to efficiently organize and manage the stored data.
- Consider indexing strategies to optimize data retrieval performance for various analytical queries.

#### 7.Streamlit Dashboard Development:
- Use Streamlit, a Python library for building interactive web applications, to develop a dashboard for data visualization and analysis.
- Connect the Streamlit dashboard to the MySQL database to fetch and display the stored YouTube data.

## User Guide
#### Step-1:
- Run the file "App.py" in terminal.
- We can see the Home page.
#### Step-2:
- Click "Data collection and Upload".
- Copy the Channel Id from Youtube( Open Youtube --> Click the Channel Name --> Click this ">" symbol and scrolldown --> click Share channel --> click "Copy channel ID").
- Paste the copied Link in the "Enter the Channel ID" box.
- Click "View Details" for Channel Details.
- After seeing the Channel Details, click the "Upload to MySQL database"("Uploading.."  message will appear with spinner.).
- Wait for the data to upload in MYSQL database.
- After the data uploaded "Channel, Videos, Comments Details are Uploaded Successfully" message will appear.  
#### Step-3:
- Click "MYSQL Database".
- Select the Channel name.
- After selecting the Channel Name, we can see the Channel Data, Video Data, Comment Data for that selected Channel.
#### Step-4:
- Click "Analyzing using SQL"
- In this page we can see "Select Your Question" box.
- There are 10 Question, we can choose one by one.
- SQL Query Output will bedisplayed as table. 

## Conclusion
  Overall, the "YouTube Data Harvesting and Warehousing using SQL and Streamlit" application offers a powerful platform for exploring and analyzing YouTube data,
  empowering users to make informed decisions and derive valuable insights from the vast repository of YouTube content.

## References
- Streamlit Documentation: [https://docs.streamlit.io/](https://docs.streamlit.io/)
- YouTube API Documentation: [https://developers.google.com/youtube](https://developers.google.com/youtube)
- SQLAlchemy Documentation: [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/)
- Python Documentation: [https://docs.python.org/](https://docs.python.org/)


  

