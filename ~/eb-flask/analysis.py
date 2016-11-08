__author__ = 'Jason'
import os, re, csv, ast, csv
import math
import jinja2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
import flask
from features import attr_str2dict
from utils import *

def _analysis(mysql,g_sty):
    disease = flask.request.form['disease']
    cuisty = str(flask.request.form['featureInfo']).strip().split()
    cui = cuisty[0]
    sty = cuisty[1]
    name = cuisty[2]
    filter_builder_tmp = flask.request.form['filter_builder']
    sql_var_str_tmp = flask.request.form['sql_var_str']
    filter_builder = decode(str(filter_builder_tmp))
    sql_var_str = decode(str(sql_var_str_tmp))
    filter_description = flask.request.form['filter_description']
    db = mysql.connect()
    cur = db.cursor()

    sql_var = sql_var_str.split("\n")
    featureName = "%s (%s)" % (name,sty )
    curr_condition = "V.task = %s and V.cui=%s and V.sty = %s"
    sql_var = [disease, cui, sty] + sql_var
    curr_tid = "SELECT distinct V.tid from cancer_cui where %s" %(curr_condition)

    # the list of trial IDs if the condition is not indexed in COMPACT
    trial_ids_with_conditions = []

    db = mysql.connect()
    cur = db.cursor()

    #sql = "SELECT distinct V.TID, V.month FROM cancer_cui V, meta T where %s" %(curr_condition) + " and T.tid = V.tid and "+ phase_query + " and "+ status_query + " and "+ study_type_query + " and "+ intervention_type_query + " and "+ agency_type_query + " and "+ gender_query + " and "+ start_date_query + " and "+ age_query + " and "+ intervention_model_query + " and "+ allocation_query + " and "+ time_perspective_query + " and "+ disease_query
    sql = "SELECT V.month,SUM(V.type='INCLUSION'), SUM(V.type='EXCLUSION') FROM cancer_cui V, meta T where %s and %s group by V.month order by month"  % (curr_condition, filter_builder)
    print (sql,sql_var)
    cur.execute(sql, sql_var)
    modal_boundary_output_simple = []
    modal_boundary_output_simple.append(["value", "INCLUSION", "EXCLUSION"])
    num_of_trials = 0
    for row in cur.fetchall():
        modal_boundary_output_simple.append([str(row[0]),int(row[1]),int(row[2])])
        num_of_trials += int(row[2])

    # pattern distribution
    sql = "SELECT V.pattern, SUM(V.type='INCLUSION'), SUM(V.type='EXCLUSION') as freq FROM cancer_cui V, meta T where %s and %s group by pattern order by freq desc"  % (curr_condition, filter_builder)
    print sql
    cur.execute(sql, sql_var)
    pattern_freq_output_simple = []
    pattern_freq_output_simple.append(["pattern", "INCLUSION","EXCLUSION"])
    for row in cur.fetchall():
        pattern_freq_output_simple.append([str(row[0]),int(row[1]),int(row[2])])

    # show the ranking of frequency of co-occurrence cui
    sql = "select C.cui,C.sty,C.org_str, count(*) as cnt from cancer_cui C join (SELECT DISTINCT V.tid as tid FROM cancer_cui V, meta T where %s and %s) D on C.tid=D.tid and  (C.nested = 'None' or C.nested = 'nesting') group by C.cui,C.sty order by cnt desc limit 100"  % (curr_condition, filter_builder)
    print (sql,sql_var)
    cur.execute(sql, sql_var)
    cooccur_freq_output_simple = []
    # cooccur_freq_output_simple.append(["term", "cui", "Semantic type","group", "frequency"])
    for row in cur.fetchall():
        cooccur_freq_output_simple.append([str(row[2]), str(row[0]),str(row[1]), g_sty[row[1]][3], g_sty[row[1]][1], int(row[3])])

    filter_dict = attr_str2dict(filter_description)
    sql_var_str = encode("\n".join(sql_var))
    filter_builder = encode(filter_builder)
    curr_condition = encode(curr_condition)

    if (len(modal_boundary_output_simple) > 0):
        return flask.render_template('analysis.html', **locals())

    return "Builder page disease %s" %disease +"; and the variable is %s" %name

