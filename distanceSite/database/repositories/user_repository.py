from database.repositories.crud_repository import CrudRepository
import random
import hashlib
import uuid


class UserRepository(CrudRepository):

    def __init__(self, connection):
        CrudRepository.__init__(self, connection)

    def get_name_similiar_users(self, name):
        select_query = "SELECT * from ourair.user where LOWER(name) like '%{0}%';".format(name.lower())
        return self.select_query(select_query)

    def get_email_similiar_users(self, email):
        select_query = "SELECT * from ourair.user where LOWER(email) like '%{0}%';".format(email.lower())
        return self.select_query(select_query)

    def get_user_details(self, user_id):
        select_text = "SELECT name, email, role from ourair.user where id={0};".format(user_id)
        return self.select_query(select_text)

    def delete_user(self, user_id):
        remove_text = "DELETE FROM ourair.user where id = {0}".format(user_id)
        self.insert_query(remove_text)


    def get_user_customers(self, user_id):
        select_text = "SELECT company.id as company_id, company.company_name as company_name, " \
                      "building.name as building_name FROM ourair.qd_user_customers user_customer " \
                      "LEFT JOIN ourair.user user_table ON user_table.id = user_customer.user_id " \
                      "LEFT JOIN ourair.company company ON company.id = user_customer.customer_id " \
                      "LEFT JOIN ourair.building building ON building.company_id = company.id " \
                      "WHERE user_table.id = {0};".format(user_id)
        return self.select_query(select_text)

    def remove_user_customer(self, user_id, customer_id):
        remove_text = "DELETE FROM ourair.qd_user_customers where user_id={0} and customer_id={1};" \
                      "DELETE FROM ourair.qd_user_facilities where user_id={0} and facility_id in " \
                      "(select id from ourair.building where company_id={1});".format(
                        user_id, customer_id)
        return self.insert_query(remove_text)

    def create_user(self, email, password, name, role):
        # First check if user already exists
        user_results = self.select_query("SELECT * from ourair.user where email='{0}';".format(email))
        if len(user_results) > 0:
            print("Email already exists!")
            return None
        # Getting first and last name if possible
        if len(name.split()) > 1:
            first_name, last_name = name.split()[0], name.split()[-1]
        else:
            first_name, last_name = name, ''
        if role == 'SALES_MANAGER':
            role_id = 2
        else:
            role_id = 1
        # Generating the hashed password
        salt_choices = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        salt = ''
        for _ in range(16):
            salt = salt + random.choice(salt_choices)
        hash_text = email + password + str(salt)
        hashed_text = hashlib.sha1(str(hash_text).encode('utf-8')).hexdigest()
        password_text = hashed_text.upper() + ":" + str(salt)
        create_user_query = "INSERT INTO ourair.user (email, password, name, role) " \
                            "VALUES ('{0}', '{1}', '{2}', '{3}') RETURNING ID;".format(email, password_text, name, role)
        success = self.insert_query(create_user_query)
        user_id = None

        if success:
            # Now getting this user id
            get_user_id_query = "SELECT id from ourair.user WHERE email = '{0}';".format(email)
            user_id_results = self.select_query(get_user_id_query)
            user_id = user_id_results[-1]['id']
            create_user_details_query = "INSERT INTO ourair.user_details " \
                                        "(user_id, firstname, lastname, language, env, user_role_id, " \
                                        "temparature_units, region, email, display_name, lat, lon, share_location) " \
                                        "VALUES ({0}, '{1}', '{2}', 'en', 'GLOBAL', {3}, 'F', 'MH', " \
                                        "'{4}', '{5}', 48, 78, true);".format(
                                            user_id, first_name, last_name, role_id, email, first_name)
            self.insert_query(create_user_details_query)
            user_units_id = str(uuid.uuid4())
            create_user_units_query = "INSERT INTO ourair.user_unit_setting " \
                                      "(id, user_id, co2, tvoc, created_at, modified_at, temperature) " \
                                      "VALUES ('{0}', {1}, 'ppm', 'ppb', (now())::timestamp(0), " \
                                      "(now())::timestamp(0), 'F');".format(user_units_id, user_id)
            self.insert_query(create_user_units_query)
        return {'success': success, 'user_id': user_id}

    def get_devices_by_facility_id(self, facility_id):
        select_query = ('SELECT d.mac_address as mac, l.name as facility_name, r.floor as floor, d.name as room '
                        'FROM ourair.device d JOIN ourair.building b on d.location_id = b.location_id '
                        'JOIN ourair.location l ON b.location_id = l.id JOIN ourair.room r  '
                        'ON b.id = r.building_id where b.id={0};'.format(facility_id))
        resulting_devs = self.select_query(select_query)
        unique_devs = list()
        for dev in resulting_devs:
            if dev not in unique_devs:
                unique_devs.append(dev)
        return unique_devs

    def add_customer_to_user(self, user_id, customer_id):
        insert_query = "INSERT INTO ourair.qd_user_customers (customer_id, user_id) " \
                       "VALUES ({0}, {1});".format(customer_id, user_id)
        return self.insert_query(insert_query)

    def add_building_to_user(self, user_id, building_id):
        insert_query = "INSERT INTO ourair.qd_user_facilities (user_id, facility_id) " \
                       "VALUES ({0}, {1});".format(user_id, building_id)
        return self.insert_query(insert_query)


# import database.connection_factory as connection_factory
# connection = connection_factory.get_connection()
#
# # Create new user
# new_user = UserRepository(connection).create_user(email='newtest@test.com', password='mike123,',
#                                                   name='mikey anoth', role='SALES_MANAGER')
#
# # Add graton to that user
# UserRepository(connection).add_customer_to_user(user_id=673, customer_id=1)
# UserRepository(connection).add_building_to_user(user_id=673, building_id=146)
#
#
# import pymysql
# from pymysql.err import OperationalError
#
#
# def query_db(query_text):
#     result = list()
#     rds_host = 'qd-prod-qlair-mysql.ckrbvwfyn8sb.us-west-2.rds.amazonaws.com'
#     username = 'root'
#     password = 'gsdf624rSDFGrty6SDFae46shfgjA'
#
#     try:
#         conn = pymysql.connect(rds_host, user=username, password=password, db='qlairdb',
#                                connect_timeout=3)
#     except OperationalError:
#         return None
#
#     try:
#         with conn.cursor() as cur:
#             cur.execute("use qlairdb")
#             cur.execute(query_text)
#             conn.commit()
#             cur.close()
#             for row in cur:
#                 result.append(list(row))
#         return result
#     except TypeError:
#         return None
#
#
# # Generating the hashed password
# email = 'newtest@test.com'
# password = 'mike123'
# name = 'mikey anoth'
# role = 'SALES_MANAGER'
# salt_choices = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# salt = ''
# for _ in range(16):
#     salt = salt + random.choice(salt_choices)
# hash_text = email + password + str(salt)
# hashed_text = hashlib.sha1(str(hash_text).encode('utf-8')).hexdigest()
# password_text = hashed_text.upper() + ":" + str(salt)
# query_db("INSERT INTO qd_users (email, name, role, password) VALUES ('{0}', '{1}', '{2}', '{3}');".format(
#                 email, name, role, password_text))
