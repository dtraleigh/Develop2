class GeoRouter:
    """
    A router to control all database operations on models in the
    cac and wake applications.
    """
    route_app_labels = {'cac', 'wake'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read cac and wake models go to geodjango_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'geodjango_db'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write cac and wake models go to geodjango_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'geodjango_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the cac or wake apps is
        involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the cac and wake apps only appear in the
        'geodjango_db' database.
        """
        if app_label in self.route_app_labels:
            return db == 'geodjango_db'
        return None
