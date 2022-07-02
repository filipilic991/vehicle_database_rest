import sys

import pandas as pd
import requests
import json

class CustomExceptions(Exception):
    pass


def check_server(cid=None):
    """
    returns True or False;
    when invoked without arguments simply checks if server responds;
    invoked with car ID checks if the ID is present in the database;
    """
    try:
        reply = requests.head('http://localhost:3000')
        # print(f"Reply: {reply.status_code} = {reply.reason}")
        if reply.status_code == requests.codes.ok:
            response = True
        else:
            response = False
        return response
    except requests.exceptions.ConnectionError:
        print(f"Connection error: {sys.exc_info()}")


def print_menu():
    """# prints user menu - nothing else happens here;"""
    print(
        "+-----------------------------------+\n"
        "|       Vintage Cars Database       |\n"
        "+-----------------------------------+\n"
        "M E N U\n"
        "=======\n"
        "1. List cars\n"
        "2. Add new car\n"
        "3. Delete car\n"
        "4. Update car\n"
        "0. Exit\n"
        "Enter your choice (0..4):")
    pass


def read_user_choice(user_choice):
    """# reads user choice and checks if it's valid;
    # returns '0', '1', '2', '3' or '4'
    """
    try:
        user_choice = user_choice
        if int(user_choice) in range(0, 5):
            return user_choice
        else:
            print("Wrong option chosen. Please input a number in range from 0 to 4.")
            raise CustomExceptions
    except ValueError as e:
        print("Wrong value entered for menu choice. Please input a number in range from 0 to 4.")
    except:
        print(sys.exc_info())


def print_header():
    # prints elegant cars table header;
    pass


def print_car(car):
    # prints one car's data in a way that fits the header;
    pass


def list_cars():
    """# gets all cars' data from server and prints it;
    # if the database is empty prints diagnostic message instead;"""
    reply = requests.get("http://localhost:3000/cars")
    reply_json = reply.json()
    if len(reply_json) == 0:
        print("Database is empty.")
    else:
        df = pd.DataFrame(reply_json)
        df['id'] = df['id'].astype(int)
        df['production_year'] = df['production_year'].astype(int)
        print(df)


def name_is_valid(name):
    """# checks if name (brand or model) is valid;
    # valid name is non-empty string containing
    # digits, letters and spaces;
    # returns True or False;"""
    validity_indicator = True
    for each_char in name:
        if each_char.isalnum() or each_char.isspace():
            continue
        else:
            validity_indicator = False
    return validity_indicator


def enter_id(mode: str = 'select') -> tuple:
    # allows user to enter car's ID and checks if it's valid;
    # valid ID consists of digits only;
    # also checks if car_id exista already in database
    # returns int;
    try:
        id = input("Enter CarID")
        if id.isdigit():
            car_id = int(id)
            # check if car_id already exists
            exists = check_car_id(car_id, mode=mode)
        else:
            print("Please enter a valid number for Car_ID")
            raise CustomExceptions
        return (car_id, exists)
    except ValueError:
        print('Please enter a valid number for Car_ID')


def enter_production_year():
    """# allows user to enter car's production year and checks if it's valid;
    # valid production year is an int from range 1900..2000;
    # returns int """
    prod_year = input("Enter production year: ")
    if prod_year.isdigit():
        if int(prod_year) in range(1900, 2022):
            return int(prod_year)
        else:
            print("Production year out of range. Valid production year is an integer from range 1900..2022 ")
            raise CustomExceptions
    else:
        print(
            "Please enter a valid number for production year. Valid production year is an integer from range 1900..2000")
        raise CustomExceptions


def enter_name(what):
    """# allows user to enter car's name (brand or model) and checks if it's valid;
    # uses name_is_valid() to check the entered name;
    # returns string or None  (if user enters an empty line);
    # argument describes which of two names is entered currently ('brand' or 'model');"""
    brand_or_model_name = what
    if name_is_valid(name=brand_or_model_name):
        return brand_or_model_name
    else:
        print(
            "Entered name contains invalid characters.Valid name is non-empty string containing digits, letters and spaces.")
        raise CustomExceptions


def enter_convertible():
    # allows user to enter Yes/No answer determining if the car is convertible;
    # returns True, False or None  (if user enters an empty line);
    conv = input("Is this car a convertible model. Type 'Yes' or 'No': ").upper()
    if conv == 'YES':
        return True
    elif conv == 'NO':
        return False
    else:
        return None


def delete_car():
    try:
        # check if car id actually exists
        id, exists = enter_id(mode='delete')
        # if the car exists try to delete it
        if exists:
            delete_req = requests.delete(f'http://localhost:3000/cars/{id}')
            print(f"Status: {delete_req.status_code}, Reason: {delete_req.reason}")
        else:
            print("Car_ID does not exist. Please enter a different Car_ID")

    except:
        print(sys.exc_info())


def input_car_data():
    """# lets user enter car data;
    # argument determines the car's ID;
    # returns  a dictionary of the following structure:
    # {'id': int, 'brand': str, 'model': str, 'production_year': int, 'convertible': bool }"""
    header_content = {'Content-Type': 'application/json'}
    id, exists = enter_id(mode='add')
    if exists:
        return None
    new_car = {'id': id,
               'brand': enter_name(what=input("Enter car's brand: ")),
               'model': enter_name(what=input("Enter car's model: ")),
               'production_year': enter_production_year(),
               'convertible': enter_convertible()}
    reply_put = requests.post('http://localhost:3000/cars', headers=header_content, data=json.dumps(new_car))
    print(f"Reply code: {reply_put.status_code}, Reason: {reply_put.reason}")
    A = 1
    pass


def check_car_id(id: int, mode: str = 'select') -> bool:
    reply = requests.get('http://localhost:3000/cars')
    cars_json = reply.json()
    # set found flag
    found = False
    # check if 'id' key exists in each dict
    for each_dict in cars_json:
        if 'id' in each_dict.keys():
            if int(each_dict['id']) == id:
                if mode == 'add':
                    print("Car_ID already exists. Please enter a different integer number.")
                    found = True
                elif mode == 'delete':
                    print("Car_ID found. You can delete it from database.")
                    found = True
                elif mode == 'update':
                    print("Car_ID found. You can update it from database.")
                    found = True

    return found


def add_car():
    """# invokes input_car_data() to gather car's info and adds it to the database;
    """
    input_car_data()
    pass


def update_car():
    """updates car info"""
    try:
        id, exists = enter_id(mode='update')
        if exists:
            header_content = {'Content-Type': 'application/json'}
            new_car = {'id': id,
                       'brand': enter_name(what=input("Enter car's brand: ")),
                       'model': enter_name(what=input("Enter car's model: ")),
                       'production_year': enter_production_year(),
                       'convertible': enter_convertible()}
            # update_req = requests.put(f'http://localhost:3000/cars/', headers=header_content, data=json.dumps(new_car))
            update_req = requests.put(f'http://localhost:3000/cars/{id}', json=new_car)
            print(f"Reply code: {update_req.status_code}, Reason: {update_req.reason}")
        else:
            print("Car_ID does not exist")
    except:
        print(sys.exc_info())



def run():
    try:
        while True:
            if not check_server():
                print("Server is not responding - quitting!")
                exit(1)
            print_menu()
            user_choice = input()
            choice = read_user_choice(user_choice)
            print(f"User choice: {choice}")
            if choice == '0':
                print("Bye!")
                exit(0)
            elif choice == '1':
                list_cars()
            elif choice == '2':
                add_car()
            elif choice == '3':
                delete_car()
            elif choice == '4':
                update_car()
    except:
        print(sys.exc_info())



if __name__ == '__main__':
    run()
