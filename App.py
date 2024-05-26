
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import googleapiclient.discovery
import pandas as pd
import json
from datetime import datetime
import mysql.connector
from sqlalchemy import create_engine
from googleapiclient.errors import HttpError
import isodate
from datetime import timedelta




#API Key connection to interact with youtube API

def Api_connect():
    api_key='Your_API_KEY'

    api_service_name = "youtube"
    api_version = "v3"
     
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey= api_key)    
     
    return youtube

youtube=Api_connect()

#mycursor and engine created to interact with MySQL Database
mydb = mysql.connector.connect(
  host="localhost",
  user="Your_User_Name",
  password="Your_Password",
  database="Your_Database_Name"
)
mycursor = mydb.cursor()
engine = create_engine("mysql+mysqlconnector://Your_User_Nmae:Your_Password@localhost/Youtube")

#To create and use the database in MySQL databse
mycursor.execute("create database if not exists Your_Database_Name")
mycursor.execute("use Your_Database_Name")



#Setting up Streamlit page
icon=Image.open('Your_File_path/YouTube.png')
st.set_page_config(page_title='YouTube data Harvesting And Warehousing',
                   page_icon=icon,
                   layout="wide",
                   initial_sidebar_state="expanded")


#Setting up streamlit sidebar menu with options
with st.sidebar:
    selected =option_menu('Main Menu',
                         ['Home','Data collection and upload','MYSQL Database','Analyzing using SQL'],
                         icons=['house','cloud-upload','database','filetype-sql'],
                         menu_icon='menu_up',
                         orientation="vertical")

#Setting up the option "Home" in streamlit page
if selected == "Home":
    st.title('_*:red[YouTube] :green[Data Harvesting and Warehousing using SQL and Streamlit]*_')    
    st.subheader(':blue[Domain :] Social Media')  
    st.subheader(':blue[Overview :]')
    st.markdown('''*Building a simple dashboard or UI using Streamlit and retrive YouTube channel data with
                   the help of the YouTube API. Stored the data in a SQL database, enabelling quering of 
                   the data using SQL within the Streamlit app.*''')   
    st.subheader(':blue[Skills Take Away :]')    
    st.markdown('*- Python scripting*')   
    st.markdown('*- Data Collection*')
    st.markdown('*- Streamlit*')
    st.markdown('*- Data Management using SQL*')

#Function to convert duration from ISO 8601 format to MySQL's datetime format 
def convert_to_mysql_datetime(PublishedAt):
    try:
        # Parse the ISO 8601 datetime string into a datetime object
        published_at_datetime = datetime.fromisoformat(PublishedAt.replace('Z', '+00:00'))
        # Format the datetime object as per MySQL's datetime format
        published_at_mysql_format = published_at_datetime.strftime('%Y-%m-%d %H:%M:%S')
        return published_at_mysql_format
    except ValueError:
        # Handle invalid datetime format
        return None

#Function to Get Channel_Details
def Channel_Details(channel_id):
    
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id= channel_id )
    response = request.execute()

    PublishedAt=response['items'][0]['snippet']['publishedAt']
    published_at_mysql_format = convert_to_mysql_datetime(PublishedAt)
    
    data={
        'Channel_Id': response['items'][0]['id'],
        'Channel_Name': response['items'][0]['snippet']['title'],
        'Channel_Thumbnail' : response['items'][0]['snippet']['thumbnails']['default']['url'],
        'Channel_Description': response['items'][0]['snippet']['description'],
        'Publisihed_Date':published_at_mysql_format,
        'Subscriber_Count':response['items'][0]['statistics']['subscriberCount'],
        'Channel_VideoCount': response['items'][0]['statistics']['videoCount'],
        'Channel_ViewCount':response['items'][0]['statistics']['viewCount'],
        'Playlist_Id':response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
         }
    return data



#Function to Get All Video_ids from Playlist_Id
def Video_ids(channel_id):
    video_ids=[]
    response=youtube.channels().list(id=channel_id,
    part='contentDetails').execute()
    
    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    next_page_token=None
    
    while True:
        response1=youtube.playlistItems().list(
        part='snippet',
        playlistId=Playlist_Id,
        pageToken=next_page_token).execute()
       
        for i in range(len(response1 ['items'])):
          video_ids.append(response1 ['items'][i]['snippet'] ['resourceId'] ['videoId'])
        
        next_page_token=response1.get('nextPageToken')
       
        if next_page_token is None:
           break
    return video_ids

#converting duration from ISO 8601 format to HH:MM:SS format
def convert_duration(duration_str):
    duration = isodate.parse_duration(duration_str)
    if isinstance(duration, timedelta):
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    else:
        return "Invalid duration"   


#Function to Get Video Details 
def Video_Details(Video_ids):

    Video_data=[]
    for video_id in Video_ids:  
        request=youtube.videos().list( 
            part= 'snippet,contentDetails,statistics',
            id=video_id
        )
        response=request.execute()

        #Changing Video 'Publishedat' format to Date time format
        PublishedAt=response['items'][0]['snippet']['publishedAt']
        published_at_mysql_format = convert_to_mysql_datetime(PublishedAt)
        
        #Converting Duration ISO 8601 format to HH:MM:SS format
        Duration= response['items'][0]['contentDetails']['duration']
        Duration= convert_duration(Duration)


        for item in response['items']:
            data={ 'Channel_Id':item['snippet']['channelId'],   
            'Video_Id':item['id'],
            'Video_Title':item['snippet']['title'],
            'Video_Description' : item['snippet']['description'],
            'Tags' : item['snippet'].get('tags'),
            'Thunbnail' : item['snippet']['thumbnails']['default']['url'],
            'Published_At' : published_at_mysql_format,
            'Duration' : Duration,
            'Caption_Status' : item['contentDetails']['caption'],
            'View_Count' : item['statistics']['viewCount'],
            'Like_Count' : item['statistics'].get('likeCount', 0),
            'Favorite_Count' : item['statistics']['favoriteCount'],
            'Comment_Count' : item['statistics'].get('commentCount')
            }
            Video_data.append(data)
    
    return Video_data
  

#Function to Get Comment Details    
def Comment_Details(Video_ids):
    Comment_data=[]
    try:
        for video_id in Video_ids:  
            request = youtube.commentThreads().list(
                    part="snippet",
                    videoId= video_id,
                    maxResults=100
                
                )
            response = request.execute()   

            for item in response['items']:
                data = {'Video_Id' : item['snippet']['topLevelComment']['snippet']['videoId'],
                        'Comment_id' : item['snippet']['topLevelComment']['id'],
                        'Comment_Text': item['snippet']['topLevelComment']['snippet']['textDisplay'],
                        'Comment_Author': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        'Comment_PublishedAt': item['snippet']['topLevelComment']['snippet']['publishedAt']
                        }

                Comment_data.append(data) 

    except:
        pass
    
    return Comment_data



#Setting up the option "Data collection and upload" in Streamlit page
if selected == "Data collection and upload":
    st.title("*_:green[Data collection and upload]_*")
    
    Channel_ID = st.text_input('**:blue[Enter the Channel ID :]**')

    if st.button("View Details"): 
        with st.spinner('Extraction in pregress...'):
            try:
                extracted_details = Channel_Details(channel_id= Channel_ID)
                st.write('**:red[Channel thumbnail]** :')
                st.image(extracted_details.get('Channel_Thumbnail'))
                st.write('**:red[Channel Name]** :', extracted_details['Channel_Name'])
                st.write('**:red[Description]** :', extracted_details['Channel_Description']) 
                st.write('**:red[Subscriber Count]** :', extracted_details['Subscriber_Count']) 
                st.write('**:red[Total Videos]** :', extracted_details['Channel_VideoCount']) 
                st.write('**:red[Total View]** :', extracted_details['Channel_ViewCount'])
                st.write('**:red[Joined]** :', extracted_details['Publisihed_Date']) 
            except HttpError as e:
                if e.resp.status == 403 and e.error_details[0]["reason"] == 'quotaExceeded':
                   st.error(" API Quota exceeded. Please try again later.")
            except KeyError as e:
                error_message = f"HTTP error occurred: {e}" # To handle specific YouTube API erroes
                st.write(error_message)
 
    if st.button("Upload to MySQl databse"):

        with st.spinner("Uploading.."):
            try:
                #To create Channel table in sql database 
                mycursor.execute(''' create table if not exists Channel(Channel_Name VARCHAR(255),
                                                                        Channel_Id VARCHAR(255) PRIMARY KEY,
                                                                        Channel_Description LONGTEXT,
                                                                        Channel_Thumbnail VARCHAR(255),
                                                                        Subscriber_Count BIGINT,
                                                                        Channel_videoCount BIGINT,
                                                                        Channel_ViewCount BIGINT,
                                                                        Playlist_Id VARCHAR(255),
                                                                        Publisihed_Date DATETIME )''') 
                #To create videos table in sql database
                mycursor.execute(''' create table if not exists Videos(Channel_Id VARCHAR(255),
                                                                    Video_Id VARCHAR(255) PRIMARY KEY,
                                                                    Video_Title VARCHAR(500),
                                                                    Video_Description LONGTEXT,
                                                                    Tags LONGTEXT,
                                                                    Thunbnail VARCHAR(255),
                                                                    Published_At  DATETIME,
                                                                    Duration TIME,
                                                                    View_Count  BIGINT,
                                                                    Like_Count BIGINT,
                                                                    Comment_Count BIGINT, 
                                                                    Favorite_Count BIGINT,
                                                                    Caption_Status VARCHAR(100),
                                                                    FOREIGN KEY (Channel_Id) REFERENCES Channel(Channel_Id) )''' )
                #To create Comments table in sql database
                mycursor.execute(''' create table if not exists Comments(Video_Id VARCHAR(255),
                                                                        Comment_id VARCHAR(255),
                                                                        Comment_Author VARCHAR(255),
                                                                        Comment_Text LONGTEXT,
                                                                        Comment_PublishedAt VARCHAR(50),
                                                                        FOREIGN KEY (Video_Id) REFERENCES Videos(Video_Id) )''')     

                #Converting datas into pandas DataFrame
                df_channel = pd.DataFrame(Channel_Details(channel_id= Channel_ID),index=[0])
                df_videos = pd.DataFrame(Video_Details(Video_ids=Video_ids(channel_id= Channel_ID))) 
                df_comments= pd.DataFrame(Comment_Details(Video_ids=Video_ids(channel_id= Channel_ID)))    

                #To load DataFrame into table in SQL Database
                df_channel.to_sql('Channel',engine,if_exists= 'append',index=False)
                df_videos['Thunbnail'] = df_videos['Thunbnail'].apply(json.dumps)
                df_videos['Tags']= df_videos['Tags'].apply(lambda x: ','.join(x) if isinstance(x, list) else '' )
                
                df_videos.to_sql('Videos',engine,if_exists= 'append',index=False)
                df_comments.to_sql('Comments',engine,if_exists= 'append',index=False)
                mydb.commit()
                st.success('Channel, Videos, Comments Details are Uploaded Successfully')
            except HttpError as e:
                error_message = f"Error retriving playlists: {e}" # To handle specific YouTube API erroes
                st.error(error_message)

#function to retrive channel name Sql DB
def Fetch_Channel_Namee(Channel_Name):
    mycursor.execute("Select Channel_Name from Channel")
    Channel_names= [row[0] for row in mycursor.fetchall()]
    return Channel_names
#funtion to fetch Channel details
def fetch_data_by_channel_name(Channel_Name):
    query = f"SELECT * FROM Channel WHERE Channel_Name = '{Channel_Name}'"
    data = pd.read_sql_query(query, engine)
    return data

#function to fetch Videos detail
def fetch_video_data_by_channel_name(Channel_Name):
    query = f"""
        SELECT v.*
        FROM Videos v
        JOIN Channel c ON c.Channel_Id = v.Channel_Id
        WHERE c.Channel_Name = '{Channel_Name}'
    """
    data = pd.read_sql_query(query, engine)
    return data
#function to fetch Comments detail
def fetch_comment_data_by_channel_name(Channel_Name):
    query = f"""
        SELECT cm.*
        FROM Comments cm
        JOIN Videos v ON cm.Video_Id = v.Video_Id
        JOIN Channel c ON c.Channel_Id = v.Channel_Id
        WHERE c.Channel_Name = '{Channel_Name}'
    """
    data = pd.read_sql_query(query, engine)
    return data

#To get Unique channel name and reads the results of an SQL query into a DataFrame 
query_unique_channels = "SELECT DISTINCT Channel_Name FROM Channel"
unique_channels = pd.read_sql_query(query_unique_channels, engine)


#Setting up the option "MYSQL Database" in streamlit page
if selected == "MYSQL Database":
    st.title("**_:green[MYSQL Database]_**")

    selected_channel = st.selectbox('Select Channel Name:', unique_channels['Channel_Name']) 
    
    #Channel table For selected Channel Name
    if selected_channel:
              data = fetch_data_by_channel_name(selected_channel)
              if not data.empty:
                st.subheader("**:blue[Channel Data]**:", selected_channel)
                st.write(data)
              else:
                st.write("No data found for the selected channel.")
    else:
        st.write("Please select a channel name.")

    #Videos table For selected Channel Name
    if selected_channel:
        video_data = fetch_video_data_by_channel_name(selected_channel)
        if not video_data.empty:
            st.subheader("**:blue[Video Data for Channel]**:", selected_channel)
            st.write(video_data)
        else:
            st.write("No video data found for the selected channel.")
    else:
        st.write("Please select a channel name.")
 
    #Comments table For selected Channel Name
    if selected_channel:
        comment_data = fetch_comment_data_by_channel_name(selected_channel)
        if not comment_data.empty:
            st.subheader("**:blue[Comment Data for Channel]**:", selected_channel)
            st.write(comment_data)
        else:
            st.write("No comment data found for the selected channel.")
    else:
        st.write("Please select a channel name.")

     
       
            
#function to execute Query for 10 questions
# 1st Question
def Sql_Question_1():
    mycursor.execute('''select Channel.Channel_name,Videos.Video_Title from videos
                        Join Channel on Channel.Channel_Id = Videos.Channel_Id
                        Order By Channel_name''')   
    out=mycursor.fetchall()
    Q1= pd.DataFrame(out, columns= ['Channel Name', 'Videos Name']).reset_index(drop=True)
    st.dataframe(Q1)                        

# 2nd Question
def Sql_Question_2():
    mycursor.execute(''' Select Distinct Channel_name, count(Videos.Video_Id) as Total_Videos
                        From Channel
                        Join Videos on Channel.Channel_Id = Videos.Channel_Id
                        Group by Channel_Name
                        Order by Total_Videos desc  ''' )
    out= mycursor.fetchall()
    Q2= pd.DataFrame(out, columns= ['Channel Name', 'total Videos']).reset_index(drop=True)
    Q2.index +=1
    st.dataframe(Q2)

# 3rd Question
def Sql_Question_3():
    mycursor.execute(''' Select Channel.Channel_Name, Videos.Video_Title, Videos.View_Count as Total_Views From Videos
                         join Channel on Channel.Channel_Id = Videos.Channel_Id
                         Order by Videos.View_Count Desc
                         limit 10''' )
    out= mycursor.fetchall()
    Q3= pd.DataFrame(out, columns= ['Channel Name', 'Videos Name', 'Total views']).reset_index(drop=True)
    Q3.index +=1
    st.dataframe(Q3) 

# 4th Question
def Sql_Question_4():
    mycursor.execute(''' Select Videos.Video_title, Videos.Comment_Count as Total_Comments
                         from Videos
                         order by Videos.Comment_Count Desc''')
    out= mycursor.fetchall()
    Q4= pd.DataFrame(out, columns= ['Videos Name', 'total Comments']).reset_index(drop=True)
    Q4.index +=1
    st.dataframe(Q4) 

# 5th Question
def Sql_Question_5():
    mycursor.execute(''' Select Channel.Channel_Name,Videos.Video_Title, Videos.Like_Count as Highest_likes from Videos
                         Join Channel on Videos.Channel_Id=Channel.Channel_Id  
                         Where Like_Count = (Select max(Videos.Like_Count) from Videos v  Where Videos.Channel_Id= v.Channel_Id
                         Group by Channel_Id )
                         order by Highest_likes desc''')
    out= mycursor.fetchall()
    Q5= pd.DataFrame(out, columns= ['Channel Name','Videos Name', 'Highest_likes']).reset_index(drop=True)
    Q5.index +=1
    st.dataframe(Q5)   

# 6th Question
def Sql_Question_6():
    mycursor.execute(''' Select Videos.Video_Title, Videos.Like_Count as Likes 
                         From Videos
                         Order by Likes Desc''' )
    out= mycursor.fetchall()
    Q6= pd.DataFrame(out, columns= ['Videos Name', 'Likes']).reset_index(drop=True)
    Q6.index +=1
    st.dataframe(Q6) 

# 7th Question
def Sql_Question_7():
    mycursor.execute(''' Select Channel.Channel_Name, Channel.Channel_ViewCount as Total_Views 
                         From Channel
                         Order by Total_Views desc''')
    out= mycursor.fetchall()
    Q7= pd.DataFrame(out, columns= ['Channel Name','Total Views']).reset_index(drop=True)
    Q7.index +=1
    st.dataframe(Q7)                      

# 8th Question
def Sql_Question_8():
    mycursor.execute(''' Select Distinct Channel.Channel_name From Channel
                         Join Videos on Videos.Channel_Id = Channel.Channel_Id
                         Where Year(Videos.Published_At) = 2022 ''')
    out= mycursor.fetchall()
    Q8= pd.DataFrame(out, columns= ['Channel Name']).reset_index(drop=True)
    Q8.index +=1
    st.dataframe(Q8) 

# 9th Question
def Sql_Question_9():
    mycursor.execute(''' Select Channel.Channel_Name, time_format(Sec_to_Time(Avg(Time_to_sec(Time(Videos.Duration)))), "%H:%i:%s")as Avg_Duration 
                         From videos
                         join Channel on Channel.Channel_Id = Videos.Channel_Id
                         Group by Channel_Name  ''')
    out= mycursor.fetchall()
    Q9= pd.DataFrame(out, columns= ['Channel Name','Average Duration']).reset_index(drop=True)
    Q9.index +=1
    st.dataframe(Q9) 

# 10th Question
def Sql_Question_10():
    mycursor.execute(''' Select Channel.Channel_Name, Videos.Video_Title, Videos.Comment_Count as Total_Comments
                         From Videos
                         Join Channel on Channel.Channel_Id = Videos.Channel_Id
                         Order By Total_Comments desc''')
    out= mycursor.fetchall()
    Q10= pd.DataFrame(out, columns= ['Channel Name','Video Name','Total_Comments']).reset_index(drop=True)
    Q10.index +=1
    st.dataframe(Q10)                     


#setting up the option "Analyzing using SQL" in streamlite page
if selected == "Analyzing using SQL":
    st.title("**_:green[Analyzing using SQL]_**") 

    Questions= ['Select Your Question',
        '1. What are the names of all the videos and their corresponding channels?',
        '2. Which channels have the most number of videos, and how many videos do they have?',
        '3. What are the top 10 most viewed videos and their respective channels?',
        '4. How many comments were made on each video, and what are their corresponding video names?',
        '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
        '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
        '7. What is the total number of views for each channel, and what are their corresponding channel names?',
        '8. What are the names of all the channels that have published videos in the year 2022?',   
        '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
        '10. Which videos have the highest number of comments, and what are their corresponding channel names?']


    selected_Question = st.selectbox(' ', options=Questions) 
    if selected_Question == '1. What are the names of all the videos and their corresponding channels?' :
        Sql_Question_1()  
    if selected_Question == '2. Which channels have the most number of videos, and how many videos do they have?' :
        Sql_Question_2()
    if selected_Question == '3. What are the top 10 most viewed videos and their respective channels?':
        Sql_Question_3()
    if selected_Question ==  '4. How many comments were made on each video, and what are their corresponding video names?':
        Sql_Question_4()
    if selected_Question == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        Sql_Question_5()
    if selected_Question == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        Sql_Question_6()
    if selected_Question == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        Sql_Question_7()
    if selected_Question == '8. What are the names of all the channels that have published videos in the year 2022?':
        Sql_Question_8()
    if selected_Question == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        Sql_Question_9()
    if selected_Question == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        Sql_Question_10()
