# coding:utf-8

class ISqlHelper(object):
    params = {'ip': None, 'port': None, 'types': None, 'protocol': None, 'country': None, 'area': None}

    def init_db(self):
        """
        Initialize the database.

        Args:
            self: (todo): write your description
        """
        raise NotImplemented

    def drop_db(self):
        """
        Drop the database.

        Args:
            self: (todo): write your description
        """
        raise NotImplemented

    def insert(self, value=None):
        """
        Inserts the given value.

        Args:
            self: (todo): write your description
            value: (todo): write your description
        """
        raise NotImplemented

    def delete(self, conditions=None):
        """
        Deletes a list.

        Args:
            self: (todo): write your description
            conditions: (todo): write your description
        """
        raise NotImplemented

    def update(self, conditions=None, value=None):
        """
        Updates conditions.

        Args:
            self: (todo): write your description
            conditions: (todo): write your description
            value: (todo): write your description
        """
        raise NotImplemented

    def select(self, count=None, conditions=None):
        """
        Select rows matching conditions.

        Args:
            self: (todo): write your description
            count: (int): write your description
            conditions: (todo): write your description
        """
        raise NotImplemented