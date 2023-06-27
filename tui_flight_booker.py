import streamlit
import pandas
import requests
import snowflake.connector
from urllib.error import URLError

streamlit.title('My Parents New Healthy Diner')
streamlit.header('Breakfast Menu')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avocado Toast')
streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')
my_fruit_list = pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit')

# Let's put a pick list here so they can pick the fruit they want to include 
fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index),['Avocado','Strawberries'])
fruits_to_show = my_fruit_list.loc[fruits_selected]

# Display the table on the page.

streamlit.dataframe(fruits_to_show)

# New section to display FruityVice API

streamlit.header("Fruityvice Fruit Advice!")

def get_fruityvice_data(fruit_choice):
    '''
    This function will get information about the specified fruit from the fruityvice website
    '''
    fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_choice}")
    # normalises the json code
    fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
    return fruityvice_normalized

try:
  fruit_choice = streamlit.text_input('What fruit would you like information about?')
  if not fruit_choice:
    streamlit.error('Please select a fruit to get information')
    
  else:
    # Converts json to dataframe
    streamlit.dataframe(get_fruityvice_data(fruit_choice))

except URLError as e:
  streamlit.error()




# Snowflake connection
streamlit.header("View Our Fruit List - Add Your Favourites!")

# snowflake related functions
def get_fruit_load_list():
    with my_cnx.cursor() as my_cur:
        my_cur.execute("SELECT * from pc_rivery_db.public.fruit_load_list")
        return my_cur.fetchall()

# Add a button to load the fruit data from Snowflake
if streamlit.button('Get Fruit Load List'):
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    streamlit.dataframe(get_fruit_load_list())
    my_cnx.close()

# Allow user to add fruits to the fruit table
def insert_row_snowflake(new_fruit):
    with my_cnx.cursor() as my_cur:
        my_cur.execute(f"insert into pc_rivery_db.public.fruit_load_list values ('{new_fruit}')")
        return "Thanks for adding " + new_fruit
        

fruit_to_add = streamlit.text_input('What fruit would you like to add?')
try:
    if not fruit_to_add:
        streamlit.error('Please select a fruit to add to the list')
    else:
        if streamlit.button('Add your Fruit to the List'):
            my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
            streamlit.text(insert_row_snowflake(fruit_to_add))
            my_cnx.close()

except URLError as e:
    streamlit.error()
