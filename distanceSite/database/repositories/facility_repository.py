from database.repositories.crud_repository import CrudRepository


class FacilityRepository(CrudRepository):

    def __init__(self, connection):
        CrudRepository.__init__(self, connection)

    def get_facility_by_id(self, fac_id):
        select_query = "SELECT * FROM ourair.building WHERE id = %s"
        results = self.query(select_query, (fac_id,))
        if len(results) == 0:
            return None
        else:
            return results[0]

    def get_customer_id_from_name(self, customer_name):
        select_query = "SELECT id from ourair.company WHERE company_name = '{0}';".format(customer_name)
        results = self.select_query(select_query)
        if len(results) == 0:
            return None
        else:
            return results[0]

    def get_customer_name_from_id(self, customer_id):
        select_query = "SELECT company_name from ourair.company WHERE id = {0};".format(customer_id)
        results = self.select_query(select_query)
        if len(results) == 0:
            return None
        else:
            return results[0]['company_name']

    def get_building_id_from_name(self, building_name):
        select_query = "SELECT id from ourair.building WHERE name='{0}';".format(building_name)
        results = self.select_query(select_query)
        if len(results) == 0:
            return None
        else:
            return results[0]

    def get_all_buildings_from_customer(self, customer_id):
        select_query = "SELECT id from ourair.building WHERE company_id = '{0}';".format(customer_id)
        results = self.select_query(select_query)
        return results

    def create_customer(self, customer_name):
        insert_query = "INSERT INTO ourair.company (company_name, company_type) " \
                       "VALUES ('{0}', 1) ;".format(customer_name)
        success = self.insert_query(insert_query)
        customer_id = None
        if success:
            customer_id_query = "SELECT id from ourair.company where company_name = '{0}';".format(customer_name)
            customer_id = self.select_query(customer_id_query)[0]['id']
        return {'success': success, 'customer_id': customer_id}

    def create_building(self, building_name, street, city, country, zipcode, customer_id):
        insert_query = "INSERT INTO ourair.building " \
                       "(name, street, city, country, pincode, company_id, status) " \
                       "VALUES ('{0}', '{1}', '{2}' ,'{3}' ,'{4}' ,'{5}', true);".format(
                        building_name, street, city, country, zipcode, customer_id)
        success = self.insert_query(insert_query)
        return success

    def create_location(self, building_id, latitude, longitude, location_name, country, address):
        insert_query = "INSERT INTO ourair.location " \
                       "(id, latitude, longitude, name, country_name, address, is_active, env) " \
                       "VALUES ('{0}', {1}, {2}, '{3}', '{4}', '{5}', true, 'GLOBAL');".format(
                        building_id, latitude, longitude, location_name, country, address)
        success = self.insert_query(insert_query)

        if success:
            # Update the building to have the id of this location
            update_query = "UPDATE ourair.building SET location_id='{0}' WHERE id = {0};".format(building_id)
            success = self.insert_query(update_query)

        return success

    def create_room(self, facility_id, room_id, room_name, floor_name):
        insert_query = "INSERT INTO ourair.room (id, name, floor, room_number, status, building_id, " \
                       "room_type_id, can_share, env, smart_control_all_device, custom_control_all_device, " \
                       "is_platform) VALUES ('{0}', '{1}', '{2}', '{3}', true, {4}, 1, false, " \
                       "'GLOBAL', false, false, false);".format(room_id, room_name, floor_name, room_name, facility_id)
        success = self.insert_query(insert_query)
        return success

    def get_facility_rooms_floors(self, facility_id):
        select_query = 'SELECT id, name, floor, room_number from ourair.room where building_id={0};'.format(facility_id)
        results = self.select_query(select_query)
        return results

    def delete_room(self, room_id):
        # Set all devices room id to none
        update_query = "UPDATE ourair.device SET room_id = null where room_id='{0}';".format(room_id)
        self.insert_query(update_query)
        delete_query = "DELETE FROM ourair.room where id='{0}'".format(room_id)
        self.insert_query(delete_query)

    def get_room_id_from_room_floor(self, building_id, room, floor):
        select_query = "SELECT id FROM ourair.room WHERE room_number='{0}' AND floor='{1}' and building_id={2};".format(
            room, floor, building_id)
        results = self.select_query(select_query)
        if len(results) == 0:
            # Try but using the name of the room instead of the room_number attribute
            select_query = "SELECT id FROM ourair.room WHERE name='{0}' AND floor='{1}' and building_id={2};".format(
                room, floor, building_id)
            results = self.select_query(select_query)
            if len(results) == 0:
                return None
            else:
                return results[0]['id']
        else:
            return results[0]['id']

    def get_all_stages(self):
        select_text = "select dict.name as stage_type, ahu.name as ahu_name, building.name as facility " \
                       "from ourair.qd_hvac_stages stage left join ourair.qd_hvac_air_handling_units ahu " \
                       "on stage.ahu_id = ahu.id left join ourair.building building " \
                       "on ahu.facility_id=building.id left join ourair.qd_hvac_stage_types_dictionary dict " \
                       "on stage.stage_type_dictionary_id=dict.id;"
        results = self.select_query(select_text)
        return results

    def get_all_stages_from_fac_id(self, fac_id):
        select_text = "SELECT stage.id as id, dict.name as stage_type, ahu.name as ahu_name, " \
                      "building.name as facility, dev.imei FROM ourair.qd_hvac_stages stage " \
                      "LEFT JOIN ourair.qd_hvac_air_handling_units ahu ON stage.ahu_id = ahu.id " \
                      "LEFT JOIN ourair.building building ON ahu.facility_id=building.id " \
                      "LEFT JOIN ourair.qd_hvac_stage_types_dictionary dict ON stage.stage_type_dictionary_id=dict.id " \
                      "LEFT JOIN ourair.qd_hvac_sensors sensor ON sensor.stage_id = stage.id " \
                      "LEFT JOIN ourair.qd_hvac_devices dev ON dev.id = sensor.device_id " \
                      "WHERE building.id={0};".format(fac_id)
        results = self.select_query(select_text)
        return results

    def get_ahu_from_imei(self, imei):
        select_text = """
        select ahu.name from ourair.qd_hvac_devices dev 
        LEFT JOIN ourair.qd_hvac_sensors sensor
        ON dev.id = sensor.device_id
        LEFT JOIN ourair.qd_hvac_stages stage
        ON stage.id = sensor.stage_id
        LEFT JOIN ourair.qd_hvac_air_handling_units ahu
        on stage.ahu_id = ahu.id where dev.imei like '%{0}%' and ahu.name is not null;""".format(imei)
        results = self.select_query(select_text)
        return results[0]['name']
