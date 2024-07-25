from collections import Counter
from datetime import date
from random import randint

class ReportGenerator:
    def __init__(self, cursor, connection, listing_items_map, report_browser):
        self.cursor = cursor
        self.connection = connection
        self.listing_items_map = listing_items_map
        self.report_browser = report_browser


    def generate_reports(self):
        today_date = date.today().strftime("%Y-%m-%d")
        report_text = ""

        report_text += "ZANITTE'S SOFTWARE\n"
        report_text += "Hochstrasse 58, Ausacker, Schleswig-Holstein\n"
        report_text += "Phone number: 04633 47 87 69\n"
        report_text += "CIF: " + ''.join(["%s" % randint(0, 9) for num in range(0, 9)]) + "\n"
        report_text += "Bank: UniCredit Bank GmbH\n"
        report_text += "IBAN: DE89 3704 0044 0532 0130 00\n"
        report_text += f"Date: {today_date}\n"
        report_text += "ZIP CODE: 24986\n"
        report_text += "Fixed tax rate: 10%\n\n"

        report_text += "\nAnalytics \n\n"

        total_tax_collected = 0
        total_sold_price = 0
        sold_makes = []
        sold_years = []
        bids_per_car = {}

        for listing_id, car_item in self.listing_items_map.items():
            if car_item.highest_bidder:
                total_sold_price += car_item.price
                sold_makes.append(car_item.make)
                sold_years.append(car_item.year)

                car_key = (car_item.make, car_item.model)
                if car_key in bids_per_car:
                    bids_per_car[car_key] += 1
                else:
                    bids_per_car[car_key] = 1

                tax = car_item.price * 0.1
                total_tax_collected += tax

        make_counter = Counter(sold_makes)
        most_popular_make, most_popular_count = make_counter.most_common(1)[0]
        most_popular_percentage = (most_popular_count / len(sold_makes)) * 100

        make_value_dict = {}
        for make, price in zip(sold_makes, [car_item.price for car_item in self.listing_items_map.values() if
                                            car_item.highest_bidder]):
            if make in make_value_dict:
                make_value_dict[make] += price
            else:
                make_value_dict[make] = price
        most_valuable_make = max(make_value_dict, key=make_value_dict.get)

        average_year = sum(sold_years) / len(sold_years) if sold_years else 0

        most_bids = max(bids_per_car.values()) if bids_per_car else 0
        most_bids_make_model = [key for key, value in bids_per_car.items() if value == most_bids]

        report_text += f"Most Popular Make Sold: {most_popular_make} ({most_popular_count} cars, {most_popular_percentage:.2f}%)\n"
        report_text += f"Most Valuable Make Sold: {most_valuable_make} (Total Value: ${make_value_dict[most_valuable_make]:.2f})\n"
        report_text += f"Average Year of Cars Sold: {average_year:.2f}\n"
        if most_bids_make_model:
            for make, model in most_bids_make_model:
                report_text += f"Most Bids Received by Make and Model: {make} {model} ({most_bids} bids)\n"
        report_text += f"Total Tax Collected: ${total_tax_collected:.2f}\n"

        report_text += "\nCars Listed (Report)\n\n"
        for listing_id, car_item in self.listing_items_map.items():
            report_text += f"Listing ID: {listing_id}\n"
            report_text += f"Make: {car_item.make}\n"
            report_text += f"Model: {car_item.model}\n"
            report_text += f"Year: {car_item.year}\n"
            report_text += f"Price: ${car_item.price}\n"
            report_text += f"Description: {car_item.description}\n\n"

        report_text += "Cars Sold (Report)\n\n"
        total_tax_collected = 0
        total_sold_price = 0
        sold_makes = []
        sold_years = []
        bids_per_car = {}

        for listing_id, car_item in self.listing_items_map.items():
            if car_item.highest_bidder:
                report_text += f"Invoice ID: {listing_id}\n"
                report_text += f"Make: {car_item.make}\n"
                report_text += f"Model: {car_item.model}\n"
                report_text += f"Year: {car_item.year}\n"
                report_text += f"Price: ${car_item.price}\n"
                report_text += f"Description: {car_item.description}\n"
                report_text += f"Highest Bidder: {car_item.highest_bidder}\n\n"



        report_text += "\nAccounts Registered (Report)\n\n"

        self.cursor.execute("SELECT id_user, username, email FROM accounts")
        accounts = self.cursor.fetchall()

        for account in accounts:
            report_text += f"User ID: {account[0]}\n"
            report_text += f"Username: {account[1]}\n"
            report_text += f"Email: {account[2]}\n\n"

        report_text += "\nAccounts which have a valid address introduced (Report)\n\n"

        self.cursor.execute("""
            SELECT accounts.username, accounts.email, user_address.city, user_address.street, user_address.number_h
            FROM accounts
            INNER JOIN user_address ON accounts.id_user = user_address.id_user
        """)
        user_addresses = self.cursor.fetchall()

        for user_address in user_addresses:
            report_text += f"Username: {user_address[0]}\n"
            report_text += f"Email: {user_address[1]}\n"
            report_text += f"City: {user_address[2]}\n"
            report_text += f"Street: {user_address[3]}\n"
            report_text += f"Number: {user_address[4]}\n\n"

        report_text += "\nUsers that have introduced a valid payment method (Report)\n\n"

        self.cursor.execute("""
                    SELECT accounts.username, accounts.email, payment_method.bank, payment_method.credit_card_number, payment_method.date, payment_method.cvv
                    FROM accounts
                    INNER JOIN payment_method ON accounts.id_user = payment_method.id_user
                """)
        user_payment_methods = self.cursor.fetchall()

        for user_payment_method in user_payment_methods:
            report_text += f"Username: {user_payment_method[0]}\n"
            report_text += f"Email: {user_payment_method[1]}\n"
            report_text += f"Bank: {user_payment_method[2]}\n"
            report_text += f"Credit Card Number: {user_payment_method[3]}\n"
            report_text += f"Date: {user_payment_method[4]}\n"
            report_text += f"CVV: {user_payment_method[5]}\n\n"

        report_text += "\nUsers that have commented (Report)\n\n"

        self.cursor.execute("""
                    SELECT comments.email, comments.comment_text, comments.timestamp, car_listings.make, car_listings.model, car_listings.year, car_listings.price, car_listings.description
                    FROM comments
                    INNER JOIN car_listings ON comments.listing_id = car_listings.listing_id
                """)
        user_comments = self.cursor.fetchall()

        for user_comment in user_comments:
            report_text += f"Email: {user_comment[0]}\n"
            report_text += f"Comment: {user_comment[1]}\n"
            report_text += f"Timestamp: {user_comment[2]}\n"
            report_text += f"Car Make: {user_comment[3]}\n"
            report_text += f"Car Model: {user_comment[4]}\n"
            report_text += f"Car Year: {user_comment[5]}\n"
            report_text += f"Car Price: {user_comment[6]}\n"
            report_text += f"Car Description: {user_comment[7]}\n\n"

        report_text += "\nUsers that have placed a bid (Report)\n\n"

        self.cursor.execute("""
                    SELECT bids.bidder_username, bids.bidder_email, bids.bid_amount, bids.bid_timestamp, car_listings.make, car_listings.model, car_listings.year, car_listings.price, car_listings.description
                    FROM bids
                    INNER JOIN car_listings ON bids.make = car_listings.make AND bids.model = car_listings.model AND bids.year = car_listings.year
                """)
        user_bids = self.cursor.fetchall()

        for user_bid in user_bids:
            report_text += f"Username: {user_bid[0]}\n"
            report_text += f"Email: {user_bid[1]}\n"
            report_text += f"Bid Amount: {user_bid[2]}\n"
            report_text += f"Bid Timestamp: {user_bid[3]}\n"
            report_text += f"Car Make: {user_bid[4]}\n"
            report_text += f"Car Model: {user_bid[5]}\n"
            report_text += f"Car Year: {user_bid[6]}\n"
            report_text += f"Car Price: {user_bid[7]}\n"
            report_text += f"Car Description: {user_bid[8]}\n\n"

        report_text += "\nUsers registered with both address and payment method completed (Report)\n\n"

        self.cursor.execute("""
                    SELECT accounts.username, accounts.email, user_address.city, user_address.street, user_address.number_h, payment_method.bank, payment_method.credit_card_number, payment_method.date, payment_method.cvv
                    FROM accounts
                    INNER JOIN user_address ON accounts.id_user = user_address.id_user
                    INNER JOIN payment_method ON accounts.id_user = payment_method.id_user
                """)
        user_registrations = self.cursor.fetchall()

        for user_registration in user_registrations:
            report_text += f"Username: {user_registration[0]}\n"
            report_text += f"Email: {user_registration[1]}\n"
            report_text += f"City: {user_registration[2]}\n"
            report_text += f"Street: {user_registration[3]}\n"
            report_text += f"Number: {user_registration[4]}\n"
            report_text += f"Bank: {user_registration[5]}\n"
            report_text += f"Credit Card Number: {user_registration[6]}\n"
            report_text += f"Date: {user_registration[7]}\n"
            report_text += f"CVV: {user_registration[8]}\n\n"

        report_text += "\nCar Listings Without Bids (Report)\n\n"

        self.cursor.execute("""
                    SELECT car_listings.make, car_listings.model, car_listings.year, car_listings.price, car_listings.description
                    FROM car_listings
                    LEFT JOIN bids ON car_listings.listing_id = bids.listing_id
                    WHERE bids.listing_id IS NULL
                """)
        car_listings_without_bids = self.cursor.fetchall()

        for car_listing in car_listings_without_bids:
            report_text += f"Make: {car_listing[0]}\n"
            report_text += f"Model: {car_listing[1]}\n"
            report_text += f"Year: {car_listing[2]}\n"
            report_text += f"Price: {car_listing[3]}\n"
            report_text += f"Description: {car_listing[4]}\n\n"

        report_text += "\nCar Listings With Comments (Report)\n\n"

        self.cursor.execute("""
                    SELECT car_listings.make, car_listings.model, car_listings.year, car_listings.price, car_listings.description, comments.username, comments.email, comments.comment_text, comments.timestamp
                    FROM car_listings
                    INNER JOIN comments ON car_listings.listing_id = comments.listing_id
                """)
        car_listings_with_comments = self.cursor.fetchall()

        for car_listing in car_listings_with_comments:
            report_text += f"Make: {car_listing[0]}\n"
            report_text += f"Model: {car_listing[1]}\n"
            report_text += f"Year: {car_listing[2]}\n"
            report_text += f"Price: {car_listing[3]}\n"
            report_text += f"Description: {car_listing[4]}\n"
            report_text += f"Commenter Username: {car_listing[5]}\n"
            report_text += f"Commenter Email: {car_listing[6]}\n"
            report_text += f"Comment: {car_listing[7]}\n"
            report_text += f"Comment Timestamp: {car_listing[8]}\n\n"


        self.report_browser.append(report_text)


        self.report_browser.setText(report_text)


        with open(f"reports_{today_date}.txt", "w", encoding='utf-8') as file:
            file.write(report_text)