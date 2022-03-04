import mysql.connector
import numpy as np

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
}


def conv_type(v):
    if np.float64 == type(v):
        return float(v), "FLOAT"
    if float == type(v):
        return v, "FLOAT"
    if int == type(v):
        return v, "INT"
    return float(v), "FLOAT"


def disassemble_dict(keyname, d: dict):
    res = []
    for k in d.keys():
        res.append([keyname + "_" + k, *conv_type(d[k])])

    return res


def disassemble_array(keyname, a):
    s = ""
    for e in a:
        s += str(e) + ", "
    return [keyname, s[:-2], "TEXT"]


def disassemble_condition(cond):
    res = []
    keys = cond.keys()
    for k in keys:
        v = cond[k]
        # dmat形式のものは除外
        if dict == type(v) and "matrix" in v:
            continue
        if dict == type(v):
            for e in disassemble_dict(k, v):
                res.append(e)
            continue
        if np.ndarray == type(v) or list == type(v):
            res.append(disassemble_array(k, v))
            continue
        # res.append([k, cond[k], type(cond[k])])
        res.append([k, *conv_type(cond[k])])

    return res


class Holder:

    data = []

    def __init__(self, absFile):
        self.read_file(absFile)

    def read_file(self, absFile):
        head = []
        with open(absFile) as f:
            line = f.readline()
            while line:
                head.append(line)
                line = f.readline()
        head = [e.replace("\n", "") for e in head]
        self.data = [e.split("\t") for e in head]

    def get(self, name):
        res = []
        for e in self.data:
            if name == e[0]:
                res = e
        return res


def get_connector(absFile):

    inf = Holder(absFile)

    user = inf.get("user")[1]
    host = inf.get("host")[1]
    password = inf.get("password")[1]
    database = inf.get("database")[1]

    con = mysql.connector.connect(
        user=user, password=password, host=host, database=database
    )

    return con


class DB:
    con = None  # connect
    cur = None  # cursor
    tableName = None  # tableName
    keyName = None  # keyName, ex. shotNumber, fileName, etc.

    info = """\
print_column_info() : カラム情報の表示

select(colName, condition, vals) : データの検索
 colName: カラム名, condition: 検索する条件式, vals: 検索する際の値
"""

    def __init__(self, absFile):
        self.open(get_connector(absFile))

    def open(self, con):
        self.con = con
        self.cur = self.con.cursor()

    def close(self):
        self.con.close()

    def commit(self):
        self.con.commit()

    def commitClose(self):
        self.commit()
        self.close()

    # 現在のカラム一覧を取得
    def getColumnNames(self):
        res = []
        self.cur.execute("SHOW COLUMNS FROM " + self.tableName)
        for v in self.cur:
            res.append(v[0])
        return res

    def print_column_info(self):
        sql = "SELECT COLUMN_NAME, COLUMN_COMMENT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s and TABLE_NAME=%s ORDER BY TABLE_NAME"
        self.cur.execute(sql, [self.con.database, self.tableName])
        a = self.cur.fetchall()
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
        sql = "SHOW TABLES FROM " + self.con.database
        self.cur.execute(sql)

        res = []
        for e in self.cur:
            res.append(e[0])
        return res

    # 使用するテーブルの指定
    def setTable(self, tableName, keyName):
        self.tableName = tableName
        self.keyName = keyName

    # テーブルの新規作成
    def makeNewTable(self, tableName, keyName, keyType):
        self.tableName = tableName
        self.keyName = keyName

        # もし既に存在しているなら削除する。
        sql = "DROP TABLE IF EXISTS " + tableName
        self.cur.execute(sql)

        sql = (
            "CREATE TABLE "
            + tableName
            + " ("
            + keyName
            + " "
            + keyType
            + " PRIMARY KEY)"
        )

        # keyTypeがテキストの時は、長さを指定する必要がある。
        if keyType == "TEXT":
            sql = (
                "CREATE TABLE "
                + tableName
                + " ("
                + keyName
                + " "
                + keyType
                + ", PRIMARY KEY("
                + keyName
                + "(255)))"
            )
            # sql = 'CREATE TABLE test (testfile TEXT, PRIMARY KEY(testfile(255)))'

        self.cur.execute(sql)

    # id (int, autoincrement)付きのテーブル作成
    def make_new_table(self, tablename):
        self.tableName = tablename
        self.keyName = "id"

        # もし既に存在しているなら削除する。
        sql = "DROP TABLE IF EXISTS " + tablename
        self.cur.execute(sql)

        sql = (
            "CREATE TABLE "
            + tablename
            + " ("
            + self.keyName
            + " INT NOT NULL AUTO_INCREMENT PRIMARY KEY)"
        )

        self.cur.execute(sql)

    # カラムの追加
    def addColumn(self, colName, colType, comment=""):
        # colType: DATETIME, DATE, TIME, INT, FLOAT, TEXT, TINYTEXT, etc.
        # comment (str)
        tableName = self.tableName
        sql = (
            "ALTER TABLE "
            + tableName
            + " ADD COLUMN "
            + colName
            + " "
            + colType
            + " COMMENT %s;"
        )
        # print(sql)
        self.cur.execute(sql, [comment])

    # 新規要素の追加
    def insert(self, keyValues):
        """テーブルへの要素の追加

         keyValuesの値を持った要素を追加する。

        Args:
            keyValues (array of keyValue): 要素の配列

        Returns:
           戻り値の型: 戻り値の説明 (例 : True なら成功, False なら失敗.)

        Raises:
            例外の名前: 例外の説明 (例 : 引数が指定されていない場合に発生 )

        Yields:
           戻り値の型: 戻り値についての説明

        Examples:

            関数の使い方について記載

            >>> print_test ("test", "message")
               test message

        Note:
            注意事項などを記載

        """
        tableName = self.tableName
        colName = self.keyName
        sql = "INSERT INTO " + tableName + " (" + colName + ") VALUES (%s)"

        for e in keyValues:
            try:
                self.cur.execute(sql, [e])
            except Exception as f:
                print("error: ", e, f)

        self.commit()

    # 要素の編集
    def update(self, keyValues, colName, colValues):
        tableName = self.tableName
        keyName = self.keyName
        sql = "UPDATE " + tableName + " SET " + colName + "=%s WHERE " + keyName + "=%s"
        for i, e in enumerate(keyValues):
            self.cur.execute(sql, [colValues[i], e])
        self.commit()

    # 要素の抽出(対象：特定カラム）
    def select(self, colName, condition=None, vals=None):  # conditionはwhere以降を記述すること
        # condition: 'date=%s'
        # vals: ['2010-07-28']
        tableName = self.tableName
        sql = "SELECT " + colName + " FROM " + tableName
        if condition != None:
            sql = "SELECT " + colName + " FROM " + tableName + " WHERE " + condition

        self.cur.execute(sql, vals)

        # res = []
        # for e in self.cur:
        #    res.append(e)
        res = self.cur.fetchall()
        return res


class DB_equilibrium(DB):
    def set_table(self, tableName):
        self.setTable(tableName, "id")
        if not self.is_exist_table():
            self.make_new_table(tableName)

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

            self.addColumn(cn, ct, cc)

    def add_data(self, dat):
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

        sql = (
            "INSERT INTO "
            + self.tableName
            + " ("
            + cnames
            + ") VALUES ("
            + stvals
            + ")"
        )
        # print(sql, vals)

        try:
            self.cur.execute(sql, vals)
        except Exception as f:
            print("error: ", e, f)

        self.commit()
