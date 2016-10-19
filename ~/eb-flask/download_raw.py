__author__ = 'Jason'
import os, re, csv, ast, csv
import math
import jinja2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
import flask


def _download_raw(mysql):
    cols_title_str = flask.request.form.get('cols_title_str',None)
    sql_data = flask.request.form.get('sql_data',None)
    input_tid = flask.request.form.get('input_tid',None)

    def generate():
        csv_result = {}
        if cols_title_str != None and sql_data != None:
            db = mysql.connect()
            cur = db.cursor()
            print sql_data
            cur.execute(str(sql_data),[str(input_tid)])
            yield str(cols_title_str) + "\n"
            for row in cur.fetchall():
                data_str = ""
                for col in row:
                    data_str += str(col) + ","
                data_str = data_str.rstrip(",")
                yield  data_str +  '\n'

    return flask.Response(generate(), mimetype='text/csv',headers={"Content-Disposition": "attachment;filename=VATEC_raw_data.csv"})

