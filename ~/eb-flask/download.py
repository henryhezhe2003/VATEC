__author__ = 'Jason'
import os, re, csv, ast, csv
import math
import jinja2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
import flask
from utils import *


def _download(mysql):
    curr_condition_tmp = flask.request.form.get('curr_condition',None)
    filter_builder_tmp = flask.request.form['filter_builder']
    sql_var_str_tmp = flask.request.form['sql_var_str']

    filter_builder = decode(str(filter_builder_tmp))
    sql_var_str = decode(str(sql_var_str_tmp))
    curr_condition = decode(str(curr_condition_tmp))
    sql_var = sql_var_str.split("\n")

    def generate():
        csv_result = {}
        if curr_condition != None and filter_builder != None:
            db = mysql.connect()
            cur = db.cursor()
            sql = "select distinct V.month,V.tid from cancer_cui V, meta T where %s and %s" % (curr_condition, filter_builder)
            print sql
            cur.execute(sql,sql_var)
            cnt = 1
            for row in cur.fetchall():
                if csv_result.get(row[0]) == None:
                    csv_result[row[0]] = row[1]
                else:
                    csv_result[row[0]] += ";" + row[1]
            for key in sorted(csv_result.keys()):
                yield str(key) + "," + str(csv_result[key]) + '\n'

    return flask.Response(generate(), mimetype='text/csv',headers={"Content-Disposition": "attachment;filename=VATEC_output.csv"})

