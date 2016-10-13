__author__ = 'Jason'
import os, re, csv, ast, csv
import math
import jinja2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
import flask

def _analysis(mysql):
    disease = flask.request.form['disease']
    cuisty = str(flask.request.form['featureInfo']).strip().split()
    cui = cuisty[0]
    sty = cuisty[1]
    name = cuisty[2]
    filter_builder = flask.request.form['filter_builder']
    db = mysql.connect()
    cur = db.cursor()

    featureName = "%s (%s)" % (name,sty )
    curr_condition = "V.task = '%s' and V.cui='%s' and V.sty = '%s'"  %(disease, cui, sty)
    curr_tid = "SELECT distinct V.tid from cancer_cui where %s" %(curr_condition)

    # the list of trial IDs if the condition is not indexed in COMPACT
    trial_ids_with_conditions = []

    db = mysql.connect()
    cur = db.cursor()

    #sql = "SELECT distinct V.TID, V.month FROM cancer_cui V, meta T where %s" %(curr_condition) + " and T.tid = V.tid and "+ phase_query + " and "+ status_query + " and "+ study_type_query + " and "+ intervention_type_query + " and "+ agency_type_query + " and "+ gender_query + " and "+ start_date_query + " and "+ age_query + " and "+ intervention_model_query + " and "+ allocation_query + " and "+ time_perspective_query + " and "+ disease_query
    sql = "SELECT V.month,SUM(V.type='INCLUSION'), SUM(V.type='EXCLUSION') FROM cancer_cui V, meta T where %s and %s group by V.month order by month"  % (curr_condition, filter_builder)
    print sql
    cur.execute(sql)
    modal_boundary_output_simple = []
    modal_boundary_output_simple.append(["value", "INCLUSION", "EXCLUSION"])
    num_of_trials = 0
    for row in cur.fetchall():
        modal_boundary_output_simple.append([str(row[0]),int(row[1]),int(row[2])])
        num_of_trials += int(row[2])

    # pattern distribution
    sql = "SELECT V.pattern, SUM(V.type='INCLUSION'), SUM(V.type='EXCLUSION') as freq FROM cancer_cui V, meta T where %s and %s group by pattern order by freq desc"  % (curr_condition, filter_builder)
    print sql
    cur.execute(sql)
    pattern_freq_output_simple = []
    pattern_freq_output_simple.append(["pattern", "INCLUSION","EXCLUSION"])
    for row in cur.fetchall():
        pattern_freq_output_simple.append([str(row[0]),int(row[1]),int(row[2])])


    if (len(modal_boundary_output_simple) > 0):
        return flask.render_template('analysis.html', **locals())

    return "Builder page disease %s" %disease +"; and the variable is %s" %name
