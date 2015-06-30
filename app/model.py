
class User(object):
    def __init__(self, user_id, email_address, supplier_id, supplier_name):
        self.id = user_id
        self.email_address = email_address
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    @staticmethod
    def from_json(user_json):
        user = user_json['users']
        supplier_id = None
        supplier_name = None
        if 'supplier' in user:
            supplier_id = user['supplier']['supplierId']
            supplier_name = user['supplier']['supplierName']
        return User(
            user_id=user['id'],
            email_address=user['emailAddress'],
            supplier_id=supplier_id,
            supplier_name=supplier_name)
