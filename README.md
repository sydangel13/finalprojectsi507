# si507finalproject

Required Python packages for this project to work:
Sqlite3
Time 
Plotly.graph_objects as go 


This project also imports two API keys from a file named secrets. The user may access their own key from the Yelp Fusion API site, as well as the EatStreet API website, in order to properly run this code. The keys I used for this project have been kept hidden so that no other users can use mine in an inappropriate manner. 


How to run the program:
After getting your API keys, the user must make sure they have sqlite3 running on their terminal. 
Next, they may run the program. 

After running the program, the user is prompted to type in a city to search, or exit. They are then asked to type in a type of food or restaurant, or exit. After typing in a statement, twenty results from Yelp come up that relate to the search. They are then prompted to select the number of the restaurant they want delivery information on, or exit. Once they select the restaurant they want to know more about, EatStreet API is used to see whether or not that restaurant delivers from EatStreet. If it does, the delivery minimum, price and phone number are displayed. They can then select their data visualization preference, based on four different options. I am using Plotly for my data visualizations -- the data options include either a scatterplot, map of the US, or a bar chart. 
