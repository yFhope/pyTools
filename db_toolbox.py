import pymysql
from pymysql import cursors
from dbutils.pooled_db import PooledDB
from loguru import logger


# TODO 功能：创建数据库连接池
class ConnectionPool(object):
    def __init__(self):
        # MySQL数据库配置
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'admin',
            'database': 'letian',
        }

    def create_pool(self):
        try:
            # 创建连接池
            pool = PooledDB(
                creator=pymysql,  # 连接驱动
                mincached=50,  # 初始化时连接池中的连接数
                maxcached=100,  # 连接池中的最大连接数
                maxconnections=32,  # 允许的最大连接数
                blocking=True,  # 连接池用完时是否阻塞，不阻塞就抛异常
                host=self.db_config['host'],
                user=self.db_config['user'],
                passwd=self.db_config['password'],
                db=self.db_config['database'],
                charset='utf8mb4',
                # cursorclass=cursors.DictCursor
            )
            return pool

        except Exception as e:
            logger.error(f"数据库连接池创建失败，异常信息: {e}")
            raise e


# TODO 用数据库连接池 封装sql的 增、删、改、查
class SQLHelper(object):
    def __init__(self):
        # 创建数据库连接池
        self.connectionpool = ConnectionPool().create_pool()

    # 封装一个公共的execute执行方法
    def execute(self, sql, param=None, autoclose=False):
        conn = None
        try:
            # 从连接池中获取一个连接对象
            conn = self.connectionpool.connection()
            with conn.cursor() as cursor:
                if param:
                    count = cursor.execute(sql, param)
                else:
                    count = cursor.execute(sql)
            # 如果是查询语句，则不运行 commit
            if not sql.lower().startswith("select"):
                conn.commit()
            if autoclose:
                conn.close()  # 归还连接对象给连接池
        except Exception as e:
            conn.rollback()  # 回滚
            conn.close()  # 释放 -> 归还连接对象给连接池
            raise e
        return conn, cursor, count

    # 查询所有
    def query_all(self, sql, param=None):
        try:
            conn, cursor, count = self.execute(sql, param, autoclose=True)
            result = cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f'query_all>>执行失败，请检查异常信息：{e}')
            raise e

    # 查询单条
    def query_one(self, sql, param=None):
        try:
            cursor, conn, count = self.execute(sql, param, autoclose=True)
            one_data = cursor.fetchone()
            return one_data
        except Exception as e:
            logger.error(f'query_one>>数据查询失败，请检查异常信息：{e}')
            raise e

    # 插入一条数据
    def insert_one(self, sql, param):
        '''
        一次新增一条数据
        :param sql:
        :param param: 列表[]或元祖()
        :return: 插入成功的数据条数
        '''
        try:
            cursor, conn, count = self.execute(sql, param, autoclose=True)
            return count
        except Exception as e:
            logger.error(f'insert_one>>插入单条数据失败，请检查异常信息：{e}')
            raise e

    # 插入多条数据
    def insert_many(self, sql, param):
        """
        :param sql:
        :param param: 列表套元祖 或 元祖套元祖  [(),()]或((),())
        :return: 插入成功的数据条数
        """
        conn = None
        try:
            # 从连接池中获取一个连接对象
            conn = self.connectionpool.connection()
            with conn.cursor() as cursor:
                count = cursor.executemany(sql, param)
                conn.commit()
                conn.close()
            return count
        except Exception as e:
            logger.error(f'insert_many>>插入多条数据失败，请检查异常信息：{e}')
            conn.rollback()
            conn.close()
            raise e

    # 删除
    def delete(self, sql, param=None):
        try:
            cursor, conn, count = self.execute(sql, param, autoclose=True)
            return count
        except Exception as e:
            msg = f'delete>>数据删除失败，请检查异常信息：{e}'
            logger.error(msg)
            raise msg

    # 更新
    def update(self, sql, param=None):
        try:
            cursor, conn, count = self.execute(sql, param, autoclose=True)
            return count
        except Exception as e:
            msg = f'update>>数据更新失败，请检查异常信息：{e}'
            logger.error(msg)
            raise msg


if __name__ == '__main__':
    # TODO 使用示例
    db = SQLHelper()
    result = db.query_all("SELECT * from pid_data")
    print(result)
