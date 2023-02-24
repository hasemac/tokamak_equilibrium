import os
import contextlib
import mysql.connector
import numpy as np
import pandas as pd

column_comments = {
    "cur_tf_tf": "current of toroidal field coil",
    "cur_tf_turn": "turn of toroidal field coil",
    "cur_ip_ip": "initial plasma current",
    "cur_ip_r0": "initial plasma position of r",
    "cur_ip_z0": "initial plasma position of z",
    "cur_ip_radius": "initial plasma radius",
    "num_dpr": "number of coefficients of dp/dx",
    "num_di2": "number of coefficients of di^2/dx",
    "error": "error value history",
    "iter": "iteration",
    "elongation": "elongation of plasma",
    "triangularity": "triangularity of plasma",
    "cal_result": "0: failure, 1: success",
    "ir_ax": "r mesh num. of magnetic axis",
    "iz_ax": "z mesh num. of magnetic axis",
    "r_ax": "r position of magnetic axis",
    "z_ax": "z position of magnetic axis",
    "conf_div": "1: divertor conf. 0: limiter conf.",
    "f_axis": "flux of magnetic axis",
    "f_surf": "flux of magnetic surface",
    "pts_r_rmin": "R where R is the smallest on the last closed flux surface",
    "pts_z_rmin": "z where R is the smallest on the last closed flux surface",
    "major_radius": "major radius",
    "minor_radius": "minor radius",
    "volume": "plasma volume",
    "cross_section": "poloidal cross section",
    "param_dp": "coefficients of dp/dx0, [0th order, 1st, 2nd, ...]",
    "param_di2": "coefficients of di^2/dx, [0th order, 1st, 2nd, ...]",
}


def disassemble(keyname, val, res):
    # dmat形式のものは除外
    if dict == type(val) and "matrix" in val:
        return
    if np.ndarray == type(val) or list == type(val) or tuple == type(val):
        s = ""
        for e in val:
            s += str(e) + ", "
        res.append([keyname, s[:-2], "TEXT"])
        return
    if np.float64 == type(val) or float == type(val):
        res.append([keyname, float(val), "FLOAT"])
        return
    if int == type(val):
        res.append([keyname, val, "INT"])
        return
    if str == type(val):
        res.append([keyname, val, "TEXT"])
        return
    if bool == type(val):
        res.append([keyname, str(val), "TEXT"])
        return
    if dict == type(val):
        for k in val.keys():
            disassemble(keyname+'_'+k, val[k], res)
        return
    

def disassemble_condition(cond):
    res = []
    for k in cond.keys():
        disassemble(k, cond[k], res)
    return res

class Db_cur:
    """接続情報が.envに記載されているcursor

    Args:
        Db_cur (class): 接続情報は.envに記載されていること
    """
    def __init__(self, database="quest", admin=False):
        self.user = os.getenv("DB_USER")
        self.host = os.getenv("DB_HOST")
        self.password = os.getenv("DB_PASS")
        self.database = os.getenv("DB_DATABASE")

    @contextlib.contextmanager
    def get_cursor(self):
        try:
            con = mysql.connector.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                database=self.database,
            )
            cur = con.cursor()
            yield cur
        finally:
            con.commit()
            con.close()
            
class DB:
    dcur = None  # cursor
    tableName = None  # tableName
    keyName = None  # keyName, ex. shotNumber, fileName, etc.

    def __init__(self, tableName='none'):
        self.dcur = Db_cur()
        self.tableName = tableName

    # 現在のカラム一覧を取得
    def getColumnNames(self):
        res = []
        with self.dcur.get_cursor() as cur:
            cur.execute(f"SHOW COLUMNS FROM {self.tableName}")
            for v in cur:
                res.append(v[0])
        return res

    def print_column_info(self):
        sql = "SELECT COLUMN_NAME, COLUMN_COMMENT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s and TABLE_NAME=%s ORDER BY TABLE_NAME"
        with self.dcur.get_cursor() as cur:
            cur.execute(sql, [self.con.database, self.tableName])
            a = cur.fetchall()
        for e in a:
            print(e[0], ":", e[1])
        return a

    # 現在のデータベース上でのテーブルの有無
    def is_exist_table(self):
        res = False
        tbs = self.getTables()
        if not self.tableName in tbs:
            return False
        return True

    # 現在のデータベース内にあるテーブル一覧
    def getTables(self):
        sql = f"SHOW TABLES FROM {self.dcur.database}"
        with self.dcur.get_cursor() as cur:
            cur.execute(sql)
            res = []
            for e in cur:
                res.append(e[0])
        return res

    # 使用するテーブルの指定
    def setTable(self, tableName, keyName):
        self.tableName = tableName
        self.keyName = keyName
    
    def set_table(self, tableName):
        self.tableName = tableName

    # テーブルの新規作成
    def makeNewTable(self, tableName, keyName, keyType):
        self.tableName = tableName
        self.keyName = keyName

        # もし既に存在しているなら削除する。
        sql0 = f"DROP TABLE IF EXISTS {tableName}"

        sql1 = f"CREATE TABLE {tableName} ({keyName} {keyType} PRIMARY KEY)"

        # keyTypeがテキストの時は、長さを指定する必要がある。
        if keyType == "TEXT":
            sql1 = f"CREATE TABLE {tableName} ({keyName} {keyType}, PRIMARY KEY({keyName}(255)))"
            # sql = 'CREATE TABLE test (testfile TEXT, PRIMARY KEY(testfile(255)))'

        with self.dcur.get_cursor() as cur:
            cur.execute(sql0)
            cur.execute(sql1)

    # id (int, autoincrement)付きのテーブル作成
    def make_new_table(self, tablename):
        self.tableName = tablename
        self.keyName = "id"

        # もし既に存在しているなら削除する。
        sql0 = f"DROP TABLE IF EXISTS {tablename}"
        sql1 = f"CREATE TABLE {tablename} ({self.keyName} INT NOT NULL AUTO_INCREMENT PRIMARY KEY)"

        with self.dcur.get_cursor() as cur:
            cur.execute(sql0)
            cur.execute(sql1)

    # カラムの追加
    def addColumn(self, colName, colType, comment=""):
        # colType: DATETIME, DATE, TIME, INT, FLOAT, TEXT, TINYTEXT, etc.
        # comment (str)
        tableName = self.tableName
        sql = f"ALTER TABLE {tableName} ADD COLUMN {colName} {colType} COMMENT %s;"
        # print(sql, comment)
        with self.dcur.get_cursor() as cur:
            cur.execute(sql, [comment])

    # 新規要素の追加
    def insert(self, keyValues):
        tableName = self.tableName
        colName = self.keyName
        sql = f"INSERT INTO {tableName} ({colName}) VALUES (%s)"

        with self.dcur.get_cursor() as cur:
            for e in keyValues:
                try:
                    cur.execute(sql, [e])
                except Exception as f:
                    print("error: ", e, f)

    # 要素の編集
    def update(self, keyValues, colName, colValues):
        tableName = self.tableName
        keyName = self.keyName
        sql = f"UPDATE {tableName} SET {colName}=%s WHERE {keyName}=%s"
        with self.dcur.get_cursor() as cur:
            for i, e in enumerate(keyValues):
                cur.execute(sql, [colValues[i], e])

    # 要素の抽出(対象：特定カラム）
    def select(self, colName, condition=None, vals=None):  # conditionはwhere以降を記述すること
        # condition: 'date=%s'
        # vals: ['2010-07-28']
        tableName = self.tableName
        sql = f"SELECT {colName} FROM {tableName}"
        if condition != None:
            sql = f"SELECT {colName} FROM {tableName} WHERE {condition}"

        with self.dcur.get_cursor() as cur:
            cur.execute(sql, vals)
            res = cur.fetchall()

        return res
    
    def select_df(self, array_col, condition, array_val):
        ar_col = array_col[:] # 浅いコピー
        if 0 == len(ar_col):
            ar_col = self.getColumnNames()
        
        # カラムの文字列作成
        sc = ""
        for e in ar_col:
            sc += e+', '
        sc = sc[:-2]
        
        dat = self.select(sc, condition, array_val)
        df = pd.DataFrame(dat, columns=ar_col)
        
        return df

    def get_next_id(self):
        sql = f'SHOW TABLE STATUS LIKE "{self.tableName}"'
        #print(sql)
        with self.dcur.get_cursor() as cur:
            cur.execute(sql)
            s = cur.fetchall()
        id = s[0][10] # ('tablename', engine, ,,,)でauto_incrementは10番目
        return id


class DB_equilibrium(DB):
    def set_table(self, tableName, comment=''):
        self.setTable(tableName, "id")
        if not self.is_exist_table():
            self.make_new_table(tableName)
            
        with self.dcur.get_cursor() as cur:
            sql = f"ALTER TABLE {tableName} COMMENT %s"
            cur.execute(sql, [comment])

    # カラムの有無の確認、無ければ作成
    def check_column(self, dat):
        com = column_comments
        cnames = self.getColumnNames()

        for e in dat:
            # 既に存在している場合
            if e[0] in cnames:
                continue

            cn = e[0]
            ct = e[2]
            cc = ""
            # コメントが存在している場合
            if cn in com.keys():
                cc = com[cn]

            # 既にカラムが存在している場合
            if cn in cnames:
                continue
            #print('try to add:'+cn)
            self.addColumn(cn, ct, cc)

    def add_data(self, dat):
        """regist dat into database
        dat = [['colname', val, 'type'],,,]
            'type': ex. 'TEXT', 'FLOAT', etc.
        Args:
            dat (list): [['colname', val, 'type'],,,]
        """
        self.check_column(dat)

        cnames = ""
        stvals = ""
        vals = []
        for e in dat:
            cnames += e[0] + ", "
            stvals += "%s, "
            vals.append(e[1])

        cnames = cnames[:-2]
        stvals = stvals[:-2]

        sql = f"INSERT INTO {self.tableName} ({cnames}) VALUES ({stvals})"

        #print(sql, vals)

        with self.dcur.get_cursor() as cur:
            cur.execute(sql, vals)

