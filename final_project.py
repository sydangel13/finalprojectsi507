 
from secrets import API_KEY
from secrets import EAT_KEY
import sqlite3
import requests
import json
import time
import plotly.graph_objects as go


CACHE_FILE_NAME = 'yelp_cache.json'
CACHE_DICT = {}

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, params, headers, cache):
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url, params=params, headers=headers)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]


# ## Load the cache, save in global variable
CACHE_DICT = load_cache()


def yelp_info(term, location, sort_by = 'review_count'):
   baseurl = 'https://api.yelp.com/v3/businesses/search'
   yelp_header = {'Authorization': 'Bearer ' + API_KEY}
   yelp_params = {'term': term, 'location': location, 'sort_by':'review_count'} 
   # 'sort_by':'rating'

   # response = requests.get(baseurl, params=yelp_params, headers = yelp_header).json()
   response = requests.get(baseurl, params=yelp_params, headers=yelp_header).json()
   make_url_request_using_cache(baseurl, params=yelp_params, headers=yelp_header, cache=CACHE_DICT)

   return response


def create_db():
   conn = sqlite3.connect('final_project.sqlite')
   cur = conn.cursor()

   # drop_yelp_info = 'DROP TABLE IF EXISTS "Yelp"'
   # drop_eat_info = 'DROP TABLE IF EXISTS "EAT"'

   create_yelp_info = '''
      CREATE TABLE IF NOT EXISTS "YELP" (
         "Id" INTEGER PRIMARY KEY AUTOINCREMENT, 
         "Name" TEXT NOT NULL, 
         "Review" INTEGER NOT NULL, 
         "Rating" INTEGER NOT NULL, 
         "Price" BLOB NOT NULL, 
         "Address" TEXT NOT NULL, 
         "City" TEXT NOT NULL, 
         "State" TEXT NOT NULL, 
         "Zipcode" INTEGER NOT NULL

      )
   '''

   create_eat_info = '''
      CREATE TABLE IF NOT EXISTS "EAT" (
         "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
         "Name" TEXT NOT NULL,
         "NumberReviews" INTEGER NOT NULL,
         "Rating" INTEGER NOT NULL, 
         "Price" BLOB NOT NULL,
         "Address" TEXT NOT NULL
      )
   '''

   # cur.execute(drop_yelp_info)
   cur.execute(create_yelp_info)
   # cur.execute(drop_eat_info)
   cur.execute(create_eat_info)
   conn.commit()
   conn.close()

def db_yelp():
   insert_loc_sql = '''
      INSERT INTO YELP
      VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)
   '''

   conn = sqlite3.connect('final_project.sqlite')
   cur = conn.cursor()
   for item in loc: 
      name = item['name']
      review = item['review_count']
      rating = item['rating']
      price = item['price']
      address = item['location']['address1']
      city = item['location']['city']
      state = item['location']['state']
      zipcode = item['location']['zip_code']

      cur.execute(insert_loc_sql,
         [
            name,
            review,
            rating, 
            price,
            address,
            city,
            state,
            zipcode
         ]
      )
   
   conn.commit()
   conn.close()

def db_eatstreet():
   insert_loc_sql = '''
      INSERT INTO EAT
      VALUES (NULL, ?, ?, ?, ?, ?)
   '''

   conn = sqlite3.connect('final_project.sqlite')
   cur = conn.cursor()
   for item in eat_details['restaurants']: 
      name = item['name']
      delivery = item['offersDelivery']
      deliveryMin = item['deliveryMin']
      deliveryPrice = item['deliveryPrice']
      phone = item['phone']

      cur.execute(insert_loc_sql,
         [
            name,
            delivery,
            deliveryMin, 
            deliveryPrice,
            phone
         ]
      )
   
   conn.commit()
   conn.close()

def eat_street_info(name, launch):
   baseurl = "https://eatstreet.com/publicapi/v1/restaurant/search?"
   eat_header = {'X-Access-Token': EAT_KEY}
   eat_params = {'search': name, 'street-address': launch} 

   response = requests.get(baseurl, params=eat_params, headers=eat_header)
   result = response.json()
   make_url_request_using_cache(baseurl, params=eat_params, headers=eat_header, cache=CACHE_DICT)

   return result
   # return response

# def pie_chart():
#    yelp_info(term, location)
#    labels = 
#    values = price
#    trace = go.Pie(labels=labels, values=values)

#    py.iplot([trace], filename='basic_pie_chart')

def map_plot(long, lat, names, search_city, food_type):
   fig = go.Figure(data=go.Scattergeo(
            locationmode = 'USA-states',
            lon = long,
            lat = lat,
            text = names,
            mode = 'markers',
            marker = dict(
               size = 8,
               opacity = .8,
               symbol = 'circle',
               line = dict(
                  width = 1,
                  color = 'rgba(102, 102, 102)'
               ),
               colorscale = 'Blues',
               colorbar_title = "Restaurants by Food Type"
            )))
   
   fig.update_layout(
      title = "Popular restaurants based on cuisin <br> (Hover for restaurant names)",
      geo = dict(
         scope = 'usa',
         projection_type ='albers usa',
         showland = True,
         landcolor = "rgb(250, 250, 250)",
         subunitcolor = "rgb(217, 217, 217)",
         countrycolor = "rgb(217, 217, 217)",
         countrywidth = 0.5,
         subunitwidth = 0.5
      ),
   )
   fig.show()

def scatter_plot(prices, names):
   fig = go.Figure()
   fig.add_trace(go.Scatter(x=prices,
                                y=names,
                                marker = dict(color="red", size=14),
                                mode='markers',
                                marker_color=reviews,
                                text=names)) 

   fig.update_layout(title="Restaurants in each price range",
                     xaxis_title = "Prices")
   fig.show()
   # labels = ['$', '$$', '$$$', '$$$$']
   # labels = prices
   # values = names
   # fig = go.Figure(data = [go.Pie(labels=labels, values=values, hole=.4)])
   # fig.show()



def scatter(ratings, reviews, names):
   fig = go.Figure()
   fig.add_trace(go.Scatter(x=ratings,
                                y=reviews,
                                marker = dict(color="blue", size=13),
                                mode='markers',
                                marker_color=reviews,
                                text=names)) 

   fig.update_layout(title="Rating of Restaurant compared to it's Reviews",
                     xaxis_title = "Average rating of restaurant",
                     yaxis_title = "Average number of reviews for restaurant")
   fig.show()

def bar_chart(prices, ratings):

   # # labels = ['$', '$$', '$$$', '$$$$']
   fig = go.Figure([go.Bar(x=prices, y=ratings)])
   fig.update_layout(title="Restaurant price compared to it's rating",
                     xaxis_title = "Price of the restaurant",
                     yaxis_title = "Rating of the restaurant")
   fig.show()
   # fig = go.Figure(data=[go.Scatter(
   #    x=prices, y=ratings,
   #    text=names,
   #    marker = dict(color = "blue", size=13),
   #    mode='markers',
   #    # marker=dict(size=15, sizemin=12,
   # )])

   # fig.show()

if __name__ == "__main__":
   create_db()
   while True:
      search_city = input("Enter a city to search or 'exit':")
      new_city = search_city.strip().lower()
      if new_city == 'exit':
         break
      food_search = input('Enter a type of food (ex: American, Chinese, Mexican) or "exit":')
      food_type = food_search.strip().lower()
      if food_type == 'exit': 
         break
      else:
         print("-------------------------------")
         print(f"{food_search} in {search_city} using Yelp")
         print("-------------------------------") 
         yelp_func = yelp_info(term=food_type, location=new_city)
         loc = yelp_func['businesses']
         counter = 1
         names = []
         reviews = []
         ratings = [] 
         graph_address = [] 
         prices = []
         lat = []
         long = []
         # print(loc)
         address_list = []
         name_list = []
         for items in loc: 
            db_yelp()
            try:
               name = items['name']
               names.append(name)
               num_reviews = items['review_count']
               reviews.append(num_reviews)
               rating = items['rating']
               ratings.append(rating)
               price = items['price']
               prices.append(price)
               latitude = items['coordinates']['latitude']
               lat.append(latitude)
               longitude = items['coordinates']['longitude']
               long.append(longitude)
               address = (items['location']['address1'])
               graph_address.append(address)
               city = (items['location']['city'])
               state = (items['location']['state'])
               zipcode = (items['location']['zip_code'])
               formatted_address = '{} {} {}, {}'.format(address, city, state, zipcode)
               address_list.append(formatted_address)
               name_list.append(name)
               print(f'[{counter}] {rating}/5: {num_reviews} total reviews. {name}. {price}. {address} {city} {state}, {zipcode}')
               counter +=1
            except KeyError: 
               price = "No price listed"
               # print(f'[{counter}] {rating}/5: {num_reviews} total reviews. {name}. {price}. {address} {city} {state}, {zipcode}')
             
         enter_number = input("Choose the number to see if they offer delivery and more details, 'exit':")
         number = enter_number.strip()
         if enter_number == 'exit':
            break
         if enter_number.isnumeric() == True: 
            int_info = int(enter_number)
            if int_info < 1:
                  print('[Error] Invalid input')
            if int_info >= counter:
                  print('[Error] Invalid input')
            else:
               launch = address_list[int_info-1]
               r_name = name_list[int_info-1]
               print("-------------------------------")
               print(f"EatStreet delivery information for {r_name}")
               print("-------------------------------") 
               eat_details = eat_street_info(r_name, launch)
               delv_price = []
               name_r = []
               for item in eat_details['restaurants']: 
                  db_eatstreet()
                  if item in eat_details['restaurants']:
                     name = item['name']
                     name_r.append(name)
                     delivery = item['offersDelivery']
                     deliveryMin = item['deliveryMin']
                     deliveryPrice = item['deliveryPrice']
                     if deliveryPrice == '':
                        deliveryPrice = "No delivery price listed"
                     delv_price.append(deliveryPrice)
                     phone = item['phone']
                     print(f"Delivery offered for {name}: {delivery}. Delivery minimum: ${deliveryMin}. Delivery price: ${deliveryPrice}. Phone: {phone}")
               if eat_details['restaurants'] == []:
                  print("EatStreet does not deliver from this restaurant. Please try a different search.")
      print("-------------------------------")
      print("Data Visualizations:")
      print("-------------------------------") 
      print(f"[1] Map of top restaurants in {search_city}, showing {food_type} cuisine.")
      print(f"[2] Scatterplot showing the price of each result for {food_type} in {search_city}.")
      print(f"[3] Scatterplot illustrating the rating vs. number of reviews.")
      print(f"[4] Bar chart illustrating the price vs. rating of {food_type} in {search_city}.")
      # while True:
      data_vis = input("Please select the number for how you would like your data to be presented, or 'exit':")
      data_number = data_vis.strip()
      if data_number == 'exit':
         break
      data_number = int(data_number)
      if data_number == 1:
         print(map_plot(long, lat, names, search_city, food_type))
      if data_number == 2: 
         print(scatter_plot(prices, names))
      if data_number == 3:
         print(scatter(ratings, reviews, names))
      if data_number == 4:
         print(bar_chart(prices, ratings))
      
         
   

   

