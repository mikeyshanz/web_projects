from database.repositories.crud_repository import CrudRepository


class APIRepository(CrudRepository):

    def __init__(self, connection):
        CrudRepository.__init__(self, connection)

    def get_devices_by_facility_id(self, facility_id):
        select_query = ('SELECT d.mac_address as mac, l.name as facility_name, r.floor as floor, d.name as room '
                        'FROM ourair.device d JOIN ourair.building b on d.location_id = b.location_id '
                        'JOIN ourair.location l ON b.location_id = l.id JOIN ourair.room r  '
                        'ON b.id = r.building_id where b.id={0};'.format(facility_id))
        return self.query(select_query, (facility_id,))

    def create_new_api(self, api_name, api_key):
        insert_text = "INSERT INTO ourair.qd_partners " \
                      "(partner_name, api_key) VALUES ('{0}', '{1}') RETURNING id;".format(api_name, api_key)
        results = self.select_query(insert_text)
        return results

    def get_partner_id_from_name(self, partner_name):
        select_text = "SELECT id from ourair.qd_partners where partner_name = '{0}';".format(partner_name)
        results = self.select_query(select_text)
        if len(results) > 0:
            return results[0]['id']

    def get_partner_name_from_id(self, partner_id):
        select_text = "SELECT partner_name FROM ourair.qd_partners where id = {0};".format(partner_id)
        return self.select_query(select_text)[0]['partner_name']

    def get_api_details(self, partner_id):
        all_facilities = "SELECT fac.id, fac.name from ourair.qd_partner_facilities partner " \
                         "LEFT JOIN ourair.building fac ON fac.id = partner.facility_id " \
                         "where partner.partner_id = {0};".format(partner_id)
        all_permissions = "SELECT perm.id, perm.name from ourair.qd_partner_permissions partner " \
                          "LEFT JOIN ourair.qd_permissions perm " \
                          "ON partner.permission_id=perm.id where partner.partner_id = {0};".format(partner_id)
        fac_results = self.select_query(all_facilities)
        perm_results = self.select_query(all_permissions)
        return {'facs': fac_results, 'permissions': perm_results}

    def list_all_api_permissions(self):
        select_text = "SELECT * from ourair.qd_permissions;"
        permissions_results = self.select_query(select_text)
        return permissions_results

    def add_api_facilities(self, facility_id, partner_id):
        insert_text = "INSERT INTO ourair.qd_partner_facilities " \
                      "(partner_id, facility_id) VALUES ({0}, {1});".format(partner_id, facility_id)
        success = self.insert_query(insert_text)
        return success

    def add_api_permission(self, permission_id_list, partner_id):
        # Delete all permissions
        delete_text = "DELETE FROM ourair.qd_partner_permissions where partner_id={0};".format(partner_id)
        self.insert_query(delete_text)

        insert_text_add = ''.join(["({0}, {1}), ".format(partner_id, perm) for perm in permission_id_list])

        # Removing the last 2 characters, which are the last comma and space
        insert_text_add = insert_text_add[0: len(insert_text_add)-2]

        # Insert all given permissions
        insert_text = "INSERT INTO ourair.qd_partner_permissions " \
                      "VALUES {0};".format(insert_text_add)
        self.insert_query(insert_text)

    def get_all_partners(self):
        select_text = "SELECT * from ourair.qd_partners;"
        results = self.select_query(select_text)
        return results

    def delete_api_key(self, partner_id):
        delete_facilities = "DELETE FROM ourair.qd_partner_facilities WHERE partner_id={0};".format(partner_id)
        delete_permissions = "DELETE FROM ourair.qd_partner_permissions WHERE partner_id={0};".format(partner_id)
        delete_key = "DELETE FROM ourair.qd_partners WHERE id={0}".format(partner_id)
        self.insert_query(delete_facilities)
        self.insert_query(delete_permissions)
        self.insert_query(delete_key)
