__author__ = 'Jason'

import os, re, csv, ast, csv
import math
import jinja2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
import flask
from utils import encode

def _show_frequent_features(mysql,g_sty):

    topk = flask.request.form['topk']
    disease = flask.request.form['disease']

    # width_option = flask.request.form.get('width_option',False)
    # fixed_width = flask.request.form.get('fixed_width',None)
    condition_option = flask.request.form.get('conditions',None)
    # plot_type = flask.request.form.get('plot_type',None)
    start_month_option = flask.request.form.get('start_month',None)
    start_year_option = flask.request.form.get('start_year',None)
    start_month_before_option = flask.request.form.get('start_month_before',None)
    start_year_before_option = flask.request.form.get('start_year_before',None)
    minimum_age_option = flask.request.form.get('minimum_age',None)
    maximum_age_option = flask.request.form.get('maximum_age',None)
    gender = flask.request.form.get('gender',None)
    # aggregate_analysis_type = flask.request.form.get('aggregate_analysis_type',None)

    phase_option = flask.request.form.getlist('phase', None)
    status_option = flask.request.form.getlist('status', None)
    study_type_option = flask.request.form.getlist('study_types', None)
    intervention_type_option = flask.request.form.getlist('intervention_types', None)
    agency_type_option = flask.request.form.getlist('agency_types', None)
    intervention_model_option = flask.request.form.getlist('intervention_model', None)
    allocation_option = flask.request.form.getlist('allocation', None)
    time_perspective_option = flask.request.form.getlist('time_perspective', None)
    pattern_option = flask.request.form.getlist('pattern_option', None)

    conditions = condition_option

    # the list of trial IDs if the condition is not indexed in COMPACT
    trial_ids_with_conditions = []

    db = mysql.connect()
    cur = db.cursor()

    filter_description = ""  # a description of the clinical trails filter that is shown on the web page.
    nest_status = " (V.nested = 'None' or V.nested = 'nesting') "

    sql_var = [disease]
    disease_query = "V.task = %s "

    # check phase option and generate part of the query
    phase_query = ""
    if (len(phase_option) == 0):
        phase_query += " ( 1=1 )"
    else:
        filter_description += "phase="
        phase_query += " ("
        for phase in phase_option:
            sql_var += ["%%%s%%" % (phase)]
            phase_query += " T.phase LIKE %s" + " OR"
            filter_description += phase + ";"
        # this is not meaningful, just to terminate the part of the query
        phase_query = phase_query.rstrip("OR") + ")"
        filter_description += "\n"

    # check status option and generate part of the query
    status_query = ""
    if (len(status_option) == 0):
        status_query += " (1=1)"
    else:
        filter_description += "status="
        status_query += " ("
        for status in status_option:
            filter_description += status + ";"
            if (status == "Open Studies"):
                status_query += " T.overall_status = 'Recruiting' OR T.overall_status = 'Not yet recruiting' OR"
            elif (status == "Closed Studies"):
                status_query += " T.overall_status = 'Active, not recruiting' OR T.overall_status = 'Active, not recruiting' OR T.overall_status = 'Completed' OR T.overall_status = 'Withdrawn' OR T.overall_status = 'Suspended' OR T.overall_status = 'Terminated' OR T.overall_status = 'Enrolling by invitation' OR"
            else:
                sql_var += [status]
                status_query += " T.overall_status = %s" + " OR"
        # this is not meaningful, just to terminate the part of the query
        status_query = status_query.rstrip("OR") + ")"
        filter_description += "\n"

    # check study type option and generate part of the query
    study_type_query = ""
    if (len(study_type_option) == 0):
        study_type_query = " (T.study_type LIKE '%%')"
    else:
        filter_description += "study_type="
        study_type_query += " ("
        for study_type in study_type_option:
            sql_var += [study_type]
            study_type_query += " T.study_type = %s" + " OR"
            filter_description += study_type + ";"
        study_type_query = study_type_query.rstrip("OR") + ")"
        filter_description += "\n"

    # check intervention type option and generate part of the query
    intervention_type_query = ""
    if (len(intervention_type_option) == 0):
        intervention_type_query = " (T.intervention_type LIKE '%%')"
    else:
        filter_description += "intervention_type="
        intervention_type_query += " ("
        for intervention_type in intervention_type_option:
            sql_var += [intervention_type]
            intervention_type_query += " T.intervention_type = %s"  + " OR"
            filter_description+= intervention_type + ";"
        intervention_type_query = intervention_type_query.rstrip("OR") + ")"
        filter_description+= "\n"

    # check agency type option and generate part of the query
    agency_type_query = ""
    if (len(agency_type_option) == 0):
        agency_type_query = " (T.agency_type LIKE '%%')"
    else:
        filter_description += "agency_type="
        agency_type_query += " ("
        for agency_type in agency_type_option:
            sql_var += ["%%%s%%" % (agency_type)]
            agency_type_query += " T.agency_type LIKE %s" + " OR"
            filter_description += agency_type+"; "
        agency_type_query = agency_type_query.rstrip("OR") + ")"
        filter_description += "\n"

    # check agency type option and generate part of the query
    if (gender == '' or gender == 'all'):
        gender_query = " (T.gender LIKE '%%')"
    else:
        sql_var += [gender]
        gender_query = " (T.gender = %s" + ")"
        filter_description += "gender=%s\n" % (gender)

    # check start_year_option start_month_option and generate start_date_query
    if (start_year_option == '' or start_month_option == '' or start_month_option == 'N/A'):
        start_date_query = " (T.start_date LIKE '%%')"
    else:
        start_date = str(start_month_option) + " " + str(start_year_option)
        sql_var += [start_date]
        start_date_query = " (STR_TO_DATE(T.start_date,'%%M %%Y') >= STR_TO_DATE(%s ,'%%M %%Y'))"
        filter_description += "start_date_from=%s %s\n" % (start_month_option, start_year_option)

    if (start_year_before_option != '' or start_month_before_option != '' or start_month_before_option == 'N/A'):
        start_date_before = str(start_month_before_option) + " " + str(start_year_before_option)
        sql_var += [start_date_before]
        start_date_query += " and (STR_TO_DATE(T.start_date,'%%M %%Y') <= STR_TO_DATE(%s, '%%M %%Y'))"
        filter_description += "start_date_end=%s %s\n" % (start_month_before_option, start_year_before_option)


    # check minimum_age, maximum_age and generate age_query

    minimum_age = -1
    maximum_age = 200
    age_query = ""

    if (minimum_age_option != ''):
        try:
            minimum_age = float(minimum_age_option)
        except TypeError:
            pass

    if (maximum_age_option != ''):
        try:
            maximum_age = float(maximum_age_option)
        except TypeError:
            pass

    if len(minimum_age_option) > 0 or len(maximum_age_option)>0:
        filter_description += "Age= [%s, %s]" % (minimum_age_option, maximum_age_option)
        age_query = " (T.minimum_age_in_year >= %s and T.maximum_age_in_year <= %s)"
        sql_var += [str(minimum_age), str(maximum_age)]
    else:
        age_query = ("1=1")

    # check intervention model option and generate part of the query
    intervention_model_query = ""
    if (len(intervention_model_option) == 0):
        intervention_model_query = " (T.intervention_model LIKE '%%')"
    else:
        filter_description += "intervention_model="
        intervention_model_query += " ("
        for intervention_model in intervention_model_option:
            sql_var += ["%%%s%%" %(intervention_model)]
            intervention_model_query += " T.intervention_model LIKE %s" + " OR"
            filter_description += intervention_model + "; "
        intervention_model_query = intervention_model_query.rstrip("OR")+")"
        filter_description += "\n"

    # check allocation option and generate part of the query
    allocation_query = ""
    if (len(allocation_option) == 0):
        allocation_query = " (T.allocation LIKE '%%')"
    else:
        filter_description += "allocation="
        allocation_query += " ("
        for allocation in allocation_option:
            sql_var += ["%%%s%%" %(allocation)]
            allocation_query += " T.allocation LIKE %s" + " OR"
            filter_description += allocation + "; "
        allocation_query = allocation_query.rstrip("OR") + ")"
        filter_description += "\n"

    # check time perspective option and generate part of the query
    time_perspective_query = ""
    if (len(time_perspective_option) == 0):
        #time_perspective_query = " (T.time_perspective LIKE '%%')"
        time_perspective_query = " (1=1)"
    else:
        filter_description += "time_perspective="
        time_perspective_query += " ("
        for time_perspective in time_perspective_option:
            sql_var += ["%%%s%%" %(time_perspective)]
            time_perspective_query += " T.time_perspective LIKE %s" + " OR"
            filter_description += time_perspective + ";"
        time_perspective_query = time_perspective_query.rstrip("OR") + ")"
        filter_description += "\n"

    # the filter of pattern
    pattern_query = ""
    if (len(pattern_option) == 0):
        pattern_query = " (1=1)"
    else:
        filter_description += "pattern="
        pattern_query += " ("
        for pt in pattern_option:
            sql_var += [pt]
            pattern_query += " V.pattern = %s" + " OR"
            filter_description += pt + ";"
        pattern_query = pattern_query.rstrip("OR") + ")" # just add a false expression
        filter_description += "\n"

    value_range_error = False

    # get the total enrollment of trials contaning the variable in the certain range
    enrollment_value = 0


    # start the aggregate analysis

    # get the total number of trials meeting the requirements
    trials_meeting_requirement = ()

    #sql = "SELECT distinct V.TID, V.month FROM cancer_cui V, meta T where %s" %(curr_condition) + " and T.tid = V.tid and "+ phase_query + " and "+ status_query + " and "+ study_type_query + " and "+ intervention_type_query + " and "+ agency_type_query + " and "+ gender_query + " and "+ start_date_query + " and "+ age_query + " and "+ intervention_model_query + " and "+ allocation_query + " and "+ time_perspective_query + " and "+ disease_query
    filter_builder = " T.tid = V.tid and " + disease_query + " and " + phase_query + " and "+ status_query + " and "+ study_type_query + " and "+ intervention_type_query + " and "+ \
                     agency_type_query + " and "+ gender_query + " and "+ start_date_query + " and "+ age_query + " and "+ intervention_model_query + " and "+ \
                     allocation_query + " and "+ time_perspective_query  + " and " + pattern_query + \
                     " and "+ nest_status
    #
    # sql = "SELECT V.month, count(*), count(distinct V.tid) FROM cancer_cui V, meta T where %s" % (filter_builder)
    # print sql

    num_trials_with_disease_sql = "select count(V.cui), count(distinct V.tid) from cancer_cui V, meta T where %s " %(filter_builder)
    cur.execute(num_trials_with_disease_sql, sql_var)
    num_trials_with_disease = ''
    num_cui_with_disease = ''
    for row in cur.fetchall():
        num_cui_with_disease = row[0]
        num_trials_with_disease = row[1]

    # fetch data for the "frequency table"
    if topk == 'all':
        topk = '100000000000' # big enough  number
    frequent_numeric_feature_sql = "select V.cui,V.sty,V.cui_str,count(*) as freq from cancer_cui V, meta T where %s group by V.cui,V.sty order by freq desc" % (filter_builder) + " limit %s "
    print (frequent_numeric_feature_sql, sql_var + [topk])
    cur.execute(frequent_numeric_feature_sql, sql_var + [int(topk)])
    distribution_numeric_features = []
    for row in cur.fetchall():
        ###cui,sty,cui_str,freq
        distribution_numeric_features.append((row[2],row[1], row[0],row[3], g_sty[row[1]][3], g_sty[row[1]][1]))

    # fetch data for the "drop list menu", only the cui with duration
    duration_feature_sql = "select V.cui,V.sty,V.cui_str,count(*) as freq from cancer_cui V, meta T where (monthstart >= 0 or monthend >= 0) and %s group by V.cui,V.sty order by freq desc "  % (filter_builder) + " limit %s "
    cur.execute(duration_feature_sql, sql_var + [int(topk)])
    duration_features = []
    for row in cur.fetchall():
        ###cui,sty,cui_str,freq
        duration_features.append((row[2],row[1], row[0],row[3]))

    filter_dict = attr_str2dict(filter_description)
    sql_var_str = encode("\n".join(sql_var))
    filter_builder = encode(filter_builder)

    if db.open:
        db.close()
    return flask.render_template('features.html', **locals())

### convert a string in format "Name1=value1\nName2=value2 ..." to a dict data structure, for further use in html page.
def attr_str2dict(attrStr=""):
    output = {}
    for pair in attrStr.split("\n"):
        tokens = pair.split("=")
        if len(tokens)>=2:
            output[str(tokens[0]).strip()] = str(tokens[1]).strip()
    return output