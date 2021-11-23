from database.repositories.crud_repository import CrudRepository
from datetime import datetime


class DeviceRepository(CrudRepository):

    def __init__(self, connection):
        CrudRepository.__init__(self, connection)

    def get_devices_by_facility_id(self, facility_id):
        select_query = "select device.id as id, device.last_measurement_time, device.mac_address as mac," \
                       " device.name as device_name, " \
                       "building.name as facility_name, room.floor as floor, room.id as room_id, room.name as room " \
                       "from ourair.room room left join ourair.device device on device.room_id = room.id " \
                       "left join ourair.building building on room.building_id = building.id " \
                       "where building.id={0};".format(facility_id)
        return self.query(select_query, (facility_id,))

    def add_trikleen(self, fac_id, device_name, install_date, bulb_install_date, mac_wifi):
        ahu_id = self.select_query(
            "INSERT INTO ourair.qd_hvac_air_handling_units (name, facility_id, qd_hvac_asset_type) "
            "VALUES ('{0}', {1}, 2) RETURNING id;".format(device_name, fac_id))[0]['id']
        stage_id = self.select_query(
            "INSERT INTO ourair.qd_hvac_stages (custom_name, ahu_id, stage_type_dictionary_id) "
            "VALUES ('{0}', {1}, 3) RETURNING id;".format(device_name, ahu_id))[0]['id']
        self.insert_query("INSERT INTO ourair.qd_hvac_filters (installation_date, stage_id, is_expired, "
                          "installation_date_uv_light) VALUES ('{0}', {1}, false, '{2}');".format(install_date,
                                                                                                  stage_id,
                                                                                                  bulb_install_date))
        device_id = self.select_query("INSERT INTO ourair.qd_hvac_devices (mac_address, imei, facility_id) "
                                      "VALUES ('{0}', '{0}', {1}) RETURNING id;".format(mac_wifi, fac_id))[0]['id']
        self.insert_query(
            "INSERT INTO ourair.qd_hvac_sensors (device_id, stage_id) VALUES ({0}, {1});".format(device_id,
                                                                                                 stage_id))

    def get_facility_trikleen_devices(self, fac_id):
        select_text = "select stag.custom_name as device_name, b.name as building_name, ahu.id as ahu_id, " \
                      "stag.id as stag_id, b.id as fac_id from ourair.qd_hvac_stages stag " \
                      "left join ourair.qd_hvac_air_handling_units ahu on stag.ahu_id = ahu.id " \
                      "left join ourair.building b on b.id = ahu.facility_id where ahu.qd_hvac_asset_type=2 " \
                      "and b.id = {0};".format(fac_id)
        return self.select_query(select_text)

    def get_unassigned_devices(self, facility_id):
        select_text = "select dev.name, dev.id, dev.mac_address as mac from ourair.device dev " \
                      "left join ourair.building build " \
                      "on dev.location_id = build.location_id where build.id = {0} " \
                      "and dev.room_id is null".format(facility_id)
        return self.select_query(select_text)

    def get_all_devices(self):
        select_query = "select device.id as id, device.mac_address as mac, device.name as device_name, " \
                       "building.name as facility_name, room.floor as floor, room.room_number as room " \
                       "from ourair.room room left join ourair.device device on device.room_id = room.id " \
                       "left join ourair.building building on room.building_id = building.id;"
        return self.query(select_query, ())

    def get_all_hvac_devices(self):
        select_query = "select device.id, device.imei, unit.name as ahu_name, building.name as facility_name " \
                       "from ourair.qd_hvac_devices device left join ourair.qd_hvac_sensors sensor " \
                       "on device.id = sensor.device_id left join ourair.qd_hvac_stages stage " \
                       "on stage.id = sensor.stage_id left join ourair.qd_hvac_air_handling_units unit " \
                       "on stage.ahu_id = unit.id left join ourair.building building " \
                       "on building.id = device.facility_id;"
        results = self.select_query(select_query)
        return results

    def get_hvac_device_from_stage_list(self, stage_id_list):
        select_query = "select device.id, device.imei, unit.name as ahu_name, building.name as facility_name " \
                       "from ourair.qd_hvac_devices device left join ourair.qd_hvac_sensors sensor " \
                       "on device.id = sensor.device_id left join ourair.qd_hvac_stages stage " \
                       "on stage.id = sensor.stage_id left join ourair.qd_hvac_air_handling_units unit " \
                       "on stage.ahu_id = unit.id left join ourair.building building " \
                       "on building.id = device.facility_id WHERE stage.id in {0};".format(stage_id_list)
        results = self.select_query(select_query)
        return results

    def get_id_from_fac_name(self, facility_name):
        select_query = ("SELECT id from ourair.building where name = '{0}';".format(facility_name))
        return self.query(select_query, (facility_name,))

    def get_facility_by_id(self, fac_id):
        select_query = "SELECT * FROM ourair.building WHERE id = %s"
        results = self.query(select_query, (fac_id,))
        if len(results) == 0:
            return None
        else:
            return results[0]

    def get_customer_from_facility_id(self, fac_id):
        select_query = "SELECT c.company_name from ourair.building b LEFT JOIN ourair.company c " \
                       "on b.company_id = c.id where b.id={0};".format(fac_id)
        return self.select_query(select_query)[0]['company_name']

    def delete_device(self, device_id):
        remove_text = "DELETE FROM ourair.device where id = '{0}'".format(device_id)
        self.insert_query(remove_text)

    def get_all_facilities(self):
        select_query = "SELECT id, name FROM ourair.building ORDER BY name;"
        results = self.select_query(select_query)
        return results

    def get_facility_from_mac(self, mac_address):
        return self.select_query("SELECT building.id, building.name, building.city, "
                                 "building.country from ourair.device dev "
                                 "LEFT JOIN ourair.building building ON dev.location_id=building.location_id "
                                 "WHERE dev.mac_address = '{0}'".format(mac_address))[0]

    def get_facility_from_imei(self, imei):
        return self.select_query("SELECT building.id, building.name, building.city, "
                                 "building.country from ourair.building building "
                                 "LEFT JOIN ourair.qd_hvac_devices dev "
                                 "ON building.id = dev.facility_id WHERE dev.imei LIKE '%{0}%'".format(imei))

    def get_all_customers(self):
        select_query = "SELECT id, company_name FROM ourair.company ORDER BY company_name;"
        results = self.select_query(select_query)
        return results

    def add_room_to_building(self, room_id, name, floor, room, building_id):
        insert_query = "INSERT INTO ourair.room " \
                       "(id, name, floor, room_number, status, building_id, room_type_id, " \
                       "can_share, env, smart_control_all_device, is_platform) " \
                       "VALUES ('{0}', '{1}', '{2}', '{3}', true, {4}, 1, false, 'GLOBAL', false, false);".format(
                        room_id, name, floor, room, building_id)
        success = self.insert_query(insert_query)
        return success

    def add_aq_device_to_facility(self, dev_id, mac, sensor_name, room_id, building_id):
        # First check if there is a device with the mac equal to this mac address ( or several )
        mac_count = self.select_query("SELECT id from ourair.device where id = '{0}';".format(mac))
        if len(mac_count) > 0:
            # Then find the one with the id equal and set it to dep
            self.insert_query("UPDATE ourair.device set id='{0}_dep{1}', mac_address='{0}_dep{1}' "
                              "where id='{2}';".format(mac, len(mac_count)+1, mac))

        # First get the location id of the building
        select_query = "SELECT location_id from ourair.building where id={0};".format(building_id)
        results = self.select_query(select_query)
        location_id = results[0]['location_id']

        insert_query = "INSERT INTO ourair.device VALUES ('{0}', NULL, '{1}', NULL, " \
                       "'{2}', '{3}', '{4}', NULL, 'Chemisense SPS 118', " \
                       "NULL, NULL, NULL, NULL, NULL, false, false, NULL, 0, 0, 0, " \
                       "NULL, NULL, false, (now())::timestamp(0) without time zone, " \
                       "(now())::timestamp(0) without time zone, true, false, 'GLOBAL', NULL, " \
                       "false, false, false, NULL, NULL, 0, NULL, NULL, 0, NULL);".format(
                        mac, mac, sensor_name, location_id, room_id)
        success = self.insert_query(insert_query)
        return success

    def get_device_details(self, mac_address):
        select_query = "select d.id as id, d.mac_address as mac, d.name as device_name, b.name as facility_name, " \
                       "r.floor as floor, r.room_number as room from ourair.device d left join ourair.room r " \
                       "ON d.room_id = r.id left join ourair.building b on b.location_id = d.location_id " \
                       "where d.mac_address='{0}';".format(mac_address)
        results = self.select_query(select_query)
        unique_results = list()
        for result in results:
            if result not in unique_results:
                unique_results.append(result)
        return unique_results

    def get_specific_device(self, device_id):
        select_query = "select d.id as id, d.mac_address as mac, d.name as device_name, b.name as facility_name, " \
                       "r.floor as floor, r.room_number as room from ourair.device d left join ourair.room r " \
                       "ON d.room_id = r.id left join ourair.building b on b.location_id = d.location_id " \
                       "where d.id='{0}';".format(device_id)
        results = self.select_query(select_query)
        return results

    def update_device_info(self, device_id, device_name, facility_id, new_room_id):
        # First get the location id of the building
        select_query = "SELECT location_id from ourair.building where id={0};".format(facility_id)
        results = self.select_query(select_query)
        location_id = results[0]['location_id']
        update_query = "UPDATE ourair.device SET name = '{0}', location_id = '{1}', " \
                       "room_id = '{2}' WHERE id = '{3}';".format(device_name, location_id, new_room_id, device_id)
        success = self.insert_query(update_query)
        return success

    def add_senzit_to_facility(self, facility_id, imei_stage):
        insert_text = "INSERT INTO ourair.qd_hvac_devices (mac_address, imei, facility_id) " \
                      "VALUES (null, '{0}', {1}) RETURNING id".format(imei_stage, facility_id)
        device_id = self.select_query(insert_text)
        return device_id[0]['id']

    def relate_senzit_to_stage(self, stage_id, device_id):
        insert_text = "INSERT INTO ourair.qd_hvac_sensors (notes, device_id, stage_id) " \
                      "VALUES (null, {0}, {1});".format(device_id, stage_id)
        success = self.insert_query(insert_text)
        return success

    def add_ahu_to_facility(self, ahu_name, facility_id):
        insert_text = "insert into ourair.qd_hvac_air_handling_units " \
                      "(name, asset_tag, room_application, unit_location, room_served, " \
                      "zone, notes, vfd, power_consumption, nominal_air_flow, maximum_air_flow, " \
                      "facility_id) VALUES ('{0}', " \
                      "null, null, null, null, null, null, 0, null, null, null, " \
                      "{1}) RETURNING id;".format(ahu_name, facility_id)
        ahu_id = self.select_query(insert_text)
        return ahu_id[0]['id']

    def add_stage_to_ahu(self, ahu_id, stage_name, stage_type):
        stage_type_id_results = self.select_query("SELECT id from ourair.qd_hvac_stage_types_dictionary "
                                                  "where name = '{0}'".format(stage_type))
        if len(stage_type_id_results) == 0:
            return None

        stage_type_id = stage_type_id_results[0]['id']
        insert_text = "INSERT INTO ourair.qd_hvac_stages (custom_name, ahu_id, stage_type_dictionary_id) " \
                      "VALUES ('{0}', {1}, {2}) RETURNING id;".format(stage_name, ahu_id, stage_type_id)
        stage_id = self.select_query(insert_text)
        if stage_id is None:
            return None
        else:
            return stage_id[0]['id']

    def add_filter_to_stage(self, stage_id, merv_rating, install_ts):
        formatted_merv_rating = 'MERV_{0}'.format(merv_rating)
        insert_text = "INSERT INTO ourair.qd_hvac_filters (nr_of_filters, merv_rating, " \
                      "life_expectancy, installation_date, " \
                      "part_number, stage_id) VALUES (1, '{0}', 12, " \
                      "'{1}', null, {2});".format(formatted_merv_rating, install_ts, stage_id)
        self.insert_query(insert_text)

    def get_senzit_from_facility(self, facility_id, formatted_imei):
        select_text = "SELECT id FROM ourair.qd_hvac_devices where imei='{0}' " \
                      "AND facility_id={1};".format(formatted_imei, facility_id)
        results = self.select_query(select_text)
        return results[0]['id']

    def get_ahu_from_facility(self, ahu_name, fac_id):
        select_text = "SELECT id from ourair.qd_hvac_air_handling_units " \
                      "WHERE name='{0}' and facility_id={1};".format(ahu_name, fac_id)
        results = self.select_query(select_text)
        if results is None:
            return None
        else:
            return results[0]['id']

    def get_stage_from_ahu(self, ahu_id, stage_custom_name):
        select_text = "SELECT id from ourair.qd_hvac_stages WHERE " \
                      "ahu_id={0} and custom_name='{1}';".format(ahu_id, stage_custom_name)
        results = self.select_query(select_text)
        return results[0]['id']
