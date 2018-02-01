import pymysql.cursors
import traceback
class mysqlpdo:
    #mysql数据库连接
    connection = pymysql.connect(host='localhost', user='root', password='', db='', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    insert_id=0
    def __init__(self,host='localhost', user='root', password='', db='socialad', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor):
        mysqlpdo.connection=pymysql.connect(host=host, user=user, password=password, db=db, charset=charset,cursorclass=cursorclass)
    #构建查询参数字符串
    #string 需要构建查询参数字符串的字符列表
    def build_query_string(self,string='',type='insert'):
        if string!='' and type=='insert':
            pre_param = ''
            pre_value = ''
            for i in string:
                if pre_param == '':
                    pre_param += '`' + i + '`'
                    pre_value += '%s'
                else:
                    pre_param += ',`' + i + '`'
                    pre_value += ',%s'
            self.query_string=pre_param
            self.query_value=pre_value
        elif string!='' and  type=='select':
            pre_string=''
            for i in string:
                if pre_string == '':
                    pre_string += '`'+i['field']+'`'+i['exp']+'%s'
                else:
                    pre_string += ' '+i['pre']+' `'+i['field']+'`'+i['exp']+'%s'
            self.where_string=pre_string
            self.query_string=' * '

    #构建插入语句
    #table 表名称 param 需要构建查询参数字符串的字符列表
    def build_insert_sql(self,table='',param=''):
        if param!='' and table!='':
            self.build_query_string(string=param)
        sql='INSERT INTO `'+table+'` ('+self.query_string+') VALUES ('+self.query_value+')'
        self.sql=sql
    #构建查询语句
    #table 表名称 param 需要构建查询参数字符串的字符列表
    #where where查询条件列表（只做简单的拼接）
    def build_select_sql(self,table='',param='',where=''):
        if table!='' and param!='' and where!='':
            self.build_query_string(string=param)
            self.build_query_string(string=where,type='select')
        self.sql='SELECT '+self.query_string+' FROM `'+table+'` WHERE '+self.where_string+' ORDER BY `id` DESC'

    #select
    def select_one(self,table='',param='',where=''):
        if where == []:
            pw = {'pre': '', 'field': 'id', 'exp': '='}
        else:
            pw = {'pre': 'AND', 'field': 'id', 'exp': '='}
        where.append(pw)
        self.build_select_sql(table=table,param=param,where=where)
        try:
            with mysqlpdo.connection.cursor() as cursor:
                sql = self.sql
                cursor.execute(sql)
                result = cursor.fetchone()
                self.result=result
        except:
            traceback.print_exc()
            mysqlpdo.connection.rollback()
        finally:
            result = ''
    #upd
    def build_upd_sql(self,table='',param='',where=''):
        if(table!='' and param!=''):
            self.sql='UPDATE `'+table+'` SET `name_cn`='+param+' WHERE `id`='+where;
        try:
            with mysqlpdo.connection.cursor() as cursor:

                sql = self.sql
                cursor.execute(sql)
                mysqlpdo.connection.commit()

        except:
            traceback.print_exc()
            mysqlpdo.connection.rollback()
        finally:
            result = ''

    #插入一条数据并且返回数据id（暂时没有找到解决办法，若条件相同，则返回最大id，为最近数据 ^_^!）
    def insert_one(self,table='',param='',data=''):
        if table!='' and param!='':
            try:
                with mysqlpdo.connection.cursor() as cursor:
                    self.build_insert_sql(table=table,param=param)
                    sql=self.sql
                    print(sql)
                    print(data)

                    cursor.execute(sql, (data))
                    mysqlpdo.connection.commit()
                with mysqlpdo.connection.cursor() as cursor:
                    where=[]
                    for i in ['create_time']:
                        if where==[]:
                            pw = {'pre': '', 'field': i, 'exp': '='}
                        else:
                            pw = {'pre': 'AND', 'field': i, 'exp': '='}
                        where.append(pw)
                    self.build_select_sql(table=table,param=param,where=where)
                    sql=self.sql
                    cursor.execute(sql, (data[len(data)-2]))
                    result = cursor.fetchone()
                    print(result);
                    mysqlpdo.insert_id=result['id'];
            except:
                traceback.print_exc()
                mysqlpdo.connection.rollback()
            finally:
                result=''


    #析构函数
    def __del__(self):
        mysqlpdo.connection.close()
