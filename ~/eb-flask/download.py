__author__ = 'Jason'
import os, re, csv, ast, csv
import math
import jinja2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
import flask


def _download(mysql):
    curr_condition = flask.request.form.get('curr_condition',None)
    filter_builder = flask.request.form.get('filter_builder',None)

    def generate():
        csv_result = []
        if curr_condition != None and filter_builder != None:
            db = mysql.connect()
            cur = db.cursor()
            sql = "select distinct V.tid from cancer_cui V, meta T where %s and %s" % (curr_condition, filter_builder)
            print sql
            cur.execute(sql)
            cnt = 1
            for row in cur.fetchall():
                csv_result += row
                yield ','.join(csv_result) + '\n'
                csv_result = []

    return flask.Response(generate(), mimetype='text/csv',headers={"Content-Disposition": "attachment;filename=VATEC_output.csv"})

