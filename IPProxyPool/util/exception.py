# coding:utf-8
import config


class Test_URL_Fail(Exception):
    def __str__(self):
        """
        Return a string representation of the interface.

        Args:
            self: (todo): write your description
        """
        str = "访问%s失败，请检查网络连接" % config.TEST_IP
        return str


class Con_DB_Fail(Exception):
    def __str__(self):
        """
        Return the string representation of the device.

        Args:
            self: (todo): write your description
        """
        str = "使用DB_CONNECT_STRING:%s--连接数据库失败" % config.DB_CONNECT_STRING
        return str
