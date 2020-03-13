from DBUtils.PooledDB import PooledDB
import pymysql

_dbservice_pool = None


class MysqlPool(object):  # 设置数据库连接池和初始化
    """
        MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现
        获取连接对象：conn = Mysql.get_connection()
        释放连接对象;conn.close()或del conn
    """

    def __init__(self, mincached=5, maxcached=14,
                 maxconnections=244, blocking=True, maxshared=0):
        """
            生成MySQL数据库连接池
        :param mincached: 最少的空闲连接数，如果空闲连接数小于这个数，pool会创建一个新的连接
        :param maxcached: 最大的空闲连接数，如果空闲连接数大于这个数，pool会关闭空闲连接
        :param maxconnections: 最大的连接数
        :param blocking: 当连接数达到最大的连接数时，在请求连接的时候，如果这个值是True，请求连接的程序会一直等待，
                          直到当前连接数小于最大连接数，如果这个值是False，会报错，
        :param maxshared: 当连接数达到这个数，新请求的连接会分享已经分配出去的连接
        """
        db_config = {
            "host": '39.105.9.20',
            "port": 3306,
            "user": 'root',
            "passwd": 'bigdata_oil',
            "db": 'cxd_test',
            "charset": 'utf8'
        }
        self.pool = PooledDB(pymysql, mincached=mincached, maxcached=maxcached, maxconnections=maxconnections,
                             blocking=blocking, maxshared=maxshared, **db_config)

    def get_connection(self):
        return self.pool.connection()

    def close(self):
        self.pool.close()

    def __del__(self):
        self.close()


# 获取mysql数据库服务器的连接
def get_dbservice_mysql_conn():  # 实例化连接池类，方便调用
    """
    :return: Object  MySQL Connection
    """
    global _dbservice_pool
    if not _dbservice_pool or not isinstance(_dbservice_pool, MysqlPool):
        _dbservice_pool = MysqlPool()
    return _dbservice_pool.get_connection()


connection = get_dbservice_mysql_conn()