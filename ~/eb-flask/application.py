import os, re, csv, ast, csv
import math
import jinja2
import collections
import xml.etree.ElementTree as xml_parser
import urllib2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
from operator import itemgetter
import flask
from flask.ext.mysql import MySQL
#from flask.ext.sqlalchemy import SQLAlchemy
#in requirements.txt add Flask-SQLAlchemy==1.0

from flask import g


mysql = MySQL()
application = flask.Flask(__name__)

# Put the credential in the config file

application.config['MYSQL_DATABASE_USER'] = 'root'
application.config['MYSQL_DATABASE_PASSWORD'] = 'HeRa@CCI@FSU'
application.config['MYSQL_DATABASE_DB'] = 'cancer'
application.config['MYSQL_DATABASE_HOST'] = 'somelab12.cci.fsu.edu'
application.config['MYSQL_DATABASE_PORT'] = 3306

mysql.init_app(application)

#db = mysql.connect()

#Set application.debug=true to enable tracebacks on Beanstalk log output.
#Make sure to remove this line before deploying to production.
application.debug=True

csv_result = []

@application.route('/', methods=['POST','GET'])
def vatec_main():
    db = mysql.connect()
    cur = db.cursor()

    disease_sql = "select distinct task from cancer_cui"
    cur.execute(disease_sql)
    diseases_list = ()
    for row in cur.fetchall():
        diseases_list += (row[0],)

    if db.open:
        db.close()

    if diseases_list is None:
        return "Failed in retrieving the list of disease."
    else:
        return flask.render_template('index.html', diseases_list=diseases_list)

@application.route('/features',methods=['POST','GET'])
def show_frequent_features():
    var, aggregator_output, minimum_value, maximum_value, lower, upper, value_range_verification_output, enrollment_value, value_spectrum_output, num_trials, phase_query, condition_query, query_used, phases, conditions, status_query, statuses, study_type_query, study_types, intervention_type_query, intervention_types, agency_type_query, agency_types, gender_query, gender, modal_boundary_output, enrollment_spectrum_output, num_of_trials_output, detail_enrollment_spectrum_output,value_spectrum_output_trial_ids, initial_value_spectrum, on_option_page, start_date_query, start_date, age_query, value_range_distribution_output,value_range_width_distribution_output, average_enrollment_spectrum_output, disease, intervention_model_query, allocation_query, intervention_models, allocations, time_perspective_query, time_perspectives, start_date_before, disease_query = '', "", '', '', '', '', '', '', "", [], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', "", "", "", "", "", "", '', '', '', '', "", "", "", '', '','','','','','','',''

    topk = flask.request.form['topk']
    disease = flask.request.form['disease']

    width_option = flask.request.form.get('width_option',False)
    fixed_width = flask.request.form.get('fixed_width',None)
    condition_option = flask.request.form.get('conditions',None)
    plot_type = flask.request.form.get('plot_type',None)
    start_month_option = flask.request.form.get('start_month',None)
    start_year_option = flask.request.form.get('start_year',None)
    start_month_before_option = flask.request.form.get('start_month_before',None)
    start_year_before_option = flask.request.form.get('start_year_before',None)
    minimum_age_option = flask.request.form.get('minimum_age',None)
    maximum_age_option = flask.request.form.get('maximum_age',None)
    gender = flask.request.form.get('gender',None)
    aggregate_analysis_type = flask.request.form.get('aggregate_analysis_type',None)

    phase_option = flask.request.form.getlist('phase', None)
    status_option = flask.request.form.getlist('status', None)
    study_type_option = flask.request.form.getlist('study_types', None)
    intervention_type_option = flask.request.form.getlist('intervention_types', None)
    agency_type_option = flask.request.form.getlist('agency_types', None)
    intervention_model_option = flask.request.form.getlist('intervention_model', None)
    allocation_option = flask.request.form.getlist('allocation', None)
    time_perspective_option = flask.request.form.getlist('time_perspective', None)

    conditions = condition_option

    # the list of trial IDs if the condition is not indexed in COMPACT
    trial_ids_with_conditions = []

    db = mysql.connect()
    cur = db.cursor()

    disease_query = ""
    if (len(condition_option) != 0):
        list_of_diseases = []
        all_diseases_query = "select distinct task from cancer_cui"
        cur.execute(all_diseases_query)
        for row in cur.fetchall():
            list_of_diseases.append(row[0])

        if condition_option in list_of_diseases:
            # generate the part of query containing the condition field
            #disease_query = " T.tid in (select tid from all_diseases_trials where disease='%s')" %condition_option
            disease_query = " (V.task='%s')" %condition_option
        else:
            # trial_ids_with_conditions only deals with disease name not in the disease_list table or multiple diseases in the condition field
            disease_query = " (T.conditions LIKE '%%')"
            trial_ids_with_conditions = get_disease_clinical_trials(condition_option)
    else:
        disease_query = " (T.conditions LIKE '%%')"

    # check phase option and generate part of the query
    phase_query = ""
    if (len(phase_option) == 0):
        phase_query += " (T.phase LIKE '%%')"
    else:
        phase_query += " ("
        for phase in phase_option:
            phase_query += " T.phase LIKE '%s'" % (phase) +" OR"
            phases += phase + "/ "
        # this is not meaningful, just to terminate the part of the query
        phase_query += " T.phase LIKE '%terminated%')"

    # check status option and generate part of the query
    if (len(status_option) == 0):
        status_query += " (T.overall_status LIKE '%%')"
    else:
        status_query += " ("
        for status in status_option:
            if (status == "Open Studies"):
                status_query += " T.overall_status = 'Recruiting' OR T.overall_status = 'Not yet recruiting' OR"
            elif (status == "Closed Studies"):
                status_query += " T.overall_status = 'Active, not recruiting' OR T.overall_status = 'Active, not recruiting' OR T.overall_status = 'Completed' OR T.overall_status = 'Withdrawn' OR T.overall_status = 'Suspended' OR T.overall_status = 'Terminated' OR T.overall_status = 'Enrolling by invitation' OR"
            else:
                status_query += " T.overall_status = '%s'" % (status) + " OR"
            statuses += status + "/ "
        # this is not meaningful, just to terminate the part of the query
        status_query += " T.overall_status LIKE '%reterminated%')"

    # check study type option and generate part of the query
    if (len(study_type_option) == 0):
        study_type_query = " (T.study_type LIKE '%%')"
    else:
        study_type_query += " ("
        for study_type in study_type_option:
            study_type_query += " T.study_type = '%s'" %(study_type) +" OR"
            study_types += study_type + "/ "
        study_type_query += " T.study_type LIKE '%terminated%')"

    # check intervention type option and generate part of the query
    if (len(intervention_type_option) == 0):
        intervention_type_query = " (T.intervention_type LIKE '%%')"
    else:
        intervention_type_query += " ("
        for intervention_type in intervention_type_option:
            intervention_type_query += " T.intervention_type = '%s'" %(intervention_type) + " OR"
            intervention_types += intervention_type + "/ "
        intervention_type_query += " T.intervention_type LIKE '%terminated%')"

    # check agency type option and generate part of the query
    if (len(agency_type_option) == 0):
        agency_type_query = " (T.agency_type LIKE '%%')"
    else:
        agency_type_query += " ("
        for agency_type in agency_type_option:
            agency_type_query += " T.agency_type LIKE '%%%s%%'" %(agency_type) + " OR"
            agency_types += agency_type + "/ "
        agency_type_query += " T.agency_type LIKE '%terminated%')"

    # check agency type option and generate part of the query
    if (gender == '' or gender == 'all'):
        gender_query = " (T.gender LIKE '%%')"
    else:
        gender_query = " (T.gender = '%s'" %(gender) + ")"

    # check start_year_option start_month_option and generate start_date_query
    if (start_year_option == '' or start_month_option == '' or start_month_option == 'N/A'):
        start_date_query = " (T.start_date LIKE '%%')"
    else:
        start_date = str(start_month_option) + " " + str(start_year_option)
        start_date_query = " (STR_TO_DATE(T.start_date,'%%M %%Y') >= STR_TO_DATE('%s'" %(start_date) +",'%M %Y'))"

    if (start_year_before_option != '' and start_month_option != ''):
        start_date_before = str(start_month_before_option) + " " + str(start_year_before_option)
        start_date_query += " and (STR_TO_DATE(T.start_date,'%%M %%Y') <= STR_TO_DATE('%s'" %(start_date_before) +",'%M %Y'))"

    # check minimum_age, maximum_age and generate age_query

    minimum_age = 0
    maximum_age = 150

    if (minimum_age_option != ''):
        try:
            minimum_age = float(minimum_age_option)
        except TypeError:
            minimum_age = 0

    if (maximum_age_option != ''):
        try:
            maximum_age = float(maximum_age_option)
        except TypeError:
            maximum_age = 150

    #age_query = " (T.minimum_age_in_year >= %.9f" %float(minimum_age) +" and T.maximum_age_in_year <= %.9f)" %float(maximum_age)
    age_query = ("1=1")


    # check intervention model option and generate part of the query
    if (len(intervention_model_option) == 0):
        intervention_model_query = " (T.intervention_model LIKE '%%')"
    else:
        intervention_model_query += " ("
        for intervention_model in intervention_model_option:
            intervention_model_query += " T.intervention_model LIKE '%%%s%%'" %(intervention_model) + " OR"
            intervention_models += intervention_model + "/ "
        intervention_model_query += " T.intervention_model LIKE '%terminated%')"

    # check allocation option and generate part of the query
    if (len(allocation_option) == 0):
        allocation_query = " (T.allocation LIKE '%%')"
    else:
        allocation_query += " ("
        for allocation in allocation_option:
            allocation_query += " T.allocation LIKE '%%%s%%'" %(allocation) + " OR"
            allocations += allocation + "/ "
        allocation_query += " T.allocation LIKE '%terminated%')"

    # check time perspective option and generate part of the query
    if (len(time_perspective_option) == 0):
        #time_perspective_query = " (T.time_perspective LIKE '%%')"
        time_perspective_query = " (1=1)"
    else:
        time_perspective_query += " ("
        for time_perspective in time_perspective_option:
            time_perspective_query += " T.time_perspective LIKE '%%%s%%'" %(time_perspective) + " OR"
            time_perspectives += time_perspective + "/ "
        time_perspective_query += " T.time_perspective LIKE '%terminated%')"

    value_range_error = False

    # get the total enrollment of trials contaning the variable in the certain range
    enrollment_value = 0


    # start the aggregate analysis

    # get the total number of trials meeting the requirements
    trials_meeting_requirement = ()


    # generate distribution of values in the certain range
    if width_option:
        width = 0
    else:
        if fixed_width is None:
            width = 0.5
        else:
            try:
                width = float(fixed_width)
            except ValueError:
                width = 0.5

    #sql = "SELECT distinct V.TID, V.month FROM cancer_cui V, meta T where %s" %(curr_condition) + " and T.tid = V.tid and "+ phase_query + " and "+ status_query + " and "+ study_type_query + " and "+ intervention_type_query + " and "+ agency_type_query + " and "+ gender_query + " and "+ start_date_query + " and "+ age_query + " and "+ intervention_model_query + " and "+ allocation_query + " and "+ time_perspective_query + " and "+ disease_query
    filter_builder = " T.tid = V.tid and "+ phase_query + " and "+ status_query + " and "+ study_type_query + " and "+ intervention_type_query + " and "+ agency_type_query + " and "+ gender_query + " and "+ start_date_query + " and "+ age_query + " and "+ intervention_model_query + " and "+ allocation_query + " and "+ time_perspective_query + " and "+ disease_query
    #
    # sql = "SELECT V.month, count(*), count(distinct V.tid) FROM cancer_cui V, meta T where %s" % (filter_builder)
    # print sql

    num_trials_with_disease_sql = "select count(V.cui) from cancer_cui V, meta T where V.task = '%s' and %s " %(disease, filter_builder)
    print(num_trials_with_disease_sql)
    cur.execute(num_trials_with_disease_sql)
    num_trials_with_disease = ''
    for row in cur.fetchall():
        num_trials_with_disease = row[0]

    if topk == 'all':
        topk = '100000000000' # big enough  number
    frequent_numeric_feature_sql = "select V.cui,V.sty,V.cui_str,count(*) as freq from cancer_cui V, meta T where task = '%s' and %s group by V.cui,V.sty order by freq desc limit %s " % (disease,filter_builder,topk)
    print frequent_numeric_feature_sql
    cur.execute(frequent_numeric_feature_sql)

    distribution_numeric_features = []
    for row in cur.fetchall():
        ###cui,sty,cui_str,freq
        distribution_numeric_features.append((row[2],row[1], row[0],row[3]))
    if db.open:
        db.close()
    return flask.render_template('features.html', **locals())




@application.route('/builder',methods=['POST','GET'])
def build_query():

    var, aggregator_output, minimum_value, maximum_value, lower, upper, value_range_verification_output, enrollment_value, value_spectrum_output, num_trials, phase_query, condition_query, query_used, phases, conditions, status_query, statuses, study_type_query, study_types, intervention_type_query, intervention_types, agency_type_query, agency_types, gender_query, gender, modal_boundary_output, enrollment_spectrum_output, num_of_trials_output, detail_enrollment_spectrum_output,value_spectrum_output_trial_ids, initial_value_spectrum, on_option_page, start_date_query, start_date, age_query, value_range_distribution_output,value_range_width_distribution_output, average_enrollment_spectrum_output, disease, intervention_model_query, allocation_query, intervention_models, allocations, time_perspective_query, time_perspectives, start_date_before = '', "", '', '', '', '', '', '', "", [], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', "", "", "", "", "", "", '', '', '', '', "", "", "", '', '','','','','','',''

    disease = flask.request.form['disease']
    typed_disease = flask.request.form['typed_disease']
    if(disease == '' and typed_disease !=''):
        disease = typed_disease

    db = mysql.connect()
    cur = db.cursor()

    curr_condition = "task = '%s'"  %(disease)
    curr_tid = "SELECT distinct tid from cancer_cui where %s" %(curr_condition)
    # get number of trials of the selected disease
    sql1 = "SELECT count(cui) FROM cancer_cui where %s " %(curr_condition)
    cur.execute(sql1)
    total_num = 0
    for row in cur.fetchall():
        total_num = int(row[0])
        aggregator_output += "There are <span style=color:red>%s</span> "  % (total_num) + " UMLS terms for condition <span style=color:red>%s</span> <br><br>" % (disease)

    # get distribution of study types
    distribution_study_type = {}
    sql3 = "SELECT T.study_type, count(*) FROM meta T WHERE T.tid in (SELECT tid from cancer_cui where %s)" %(curr_condition)  + " GROUP BY T.study_type"
    cur.execute(sql3)
    for row3 in cur.fetchall():
        study_type = row3[0]
        percentage_study_type = "%.2f" %(float(row3[1])/total_num * 100)
        distribution_study_type[study_type] = percentage_study_type

    if "Interventional" not in distribution_study_type:
        distribution_study_type["Interventional"] = "0"
    if "Observational" not in distribution_study_type:
        distribution_study_type["Observational"] = "0"
    if "Observational [Patient Registry]" not in distribution_study_type:
        distribution_study_type["Observational [Patient Registry]"] = "0"
    if "Expanded Access" not in distribution_study_type:
        distribution_study_type["Expanded Access"] = "0"

    # get distribution of intervention types
    distribution_intervention_type = {}
    sql4_all = "SELECT COUNT(DISTINCT TID) FROM meta T WHERE intervention_type !='' AND TID in (%s)" % (curr_tid)
    cur.execute(sql4_all)
    for row4_all in cur.fetchall():
        num_trials_with_intervention_type = int(row4_all[0])

    sql4 = "SELECT T.intervention_type, count(*) FROM meta T WHERE T.tid in (%s)" %(curr_tid) +" GROUP BY T.intervention_type"
    cur.execute(sql4)
    for row4 in cur.fetchall():
        intervention_type = row4[0]
        percentage_intervention_type = "%.2f" %(float(row4[1])/num_trials_with_intervention_type * 100)
        distribution_intervention_type[intervention_type] = percentage_intervention_type

    if "Drug" not in distribution_intervention_type:
        distribution_intervention_type["Drug"] = "0"
    if "Procedure" not in distribution_intervention_type:
        distribution_intervention_type["Procedure"] = "0"
    if "Biological" not in distribution_intervention_type:
        distribution_intervention_type["Biological"] = "0"
    if "Device" not in distribution_intervention_type:
        distribution_intervention_type["Device"] = "0"
    if "Behavioral" not in distribution_intervention_type:
        distribution_intervention_type["Behavioral"] = "0"
    if "Dietary Supplement" not in distribution_intervention_type:
        distribution_intervention_type["Dietary Supplement"] = "0"
    if "Genetic" not in distribution_intervention_type:
        distribution_intervention_type["Genetic"] = "0"
    if "Radiation" not in distribution_intervention_type:
        distribution_intervention_type["Radiation"] = "0"
    if "Other" not in distribution_intervention_type:
        distribution_intervention_type["Other"] = "0"

    # get distribution of status
    distribution_status = {}
    sql5 = "SELECT T.overall_status, count(*) FROM meta T WHERE T.tid in (%s)" %(curr_tid) + " GROUP BY T.overall_status"
    cur.execute(sql5)
    for row5 in cur.fetchall():
        status = row5[0]
        percentage_status = "%.2f" %(float(row5[1])/total_num * 100)
        distribution_status[status] = percentage_status

    if "Recruiting" not in distribution_status:
        distribution_status["Recruiting"] = "0"
    if "Not yet recruiting" not in distribution_status:
        distribution_status["Not yet recruiting"] = "0"
    if "Active, not recruiting" not in distribution_status:
        distribution_status["Active, not recruiting"] = "0"
    if "Completed" not in distribution_status:
        distribution_status["Completed"] = "0"
    if "Withdrawn" not in distribution_status:
        distribution_status["Withdrawn"] = "0"
    if "Suspended" not in distribution_status:
        distribution_status["Suspended"] = "0"
    if "Terminated" not in distribution_status:
        distribution_status["Terminated"] = "0"
    if "Enrolling by invitation" not in distribution_status:
        distribution_status["Enrolling by invitation"] = "0"

    # get distribution of sponsor type
    distribution_sponsor_type = {}
    sql6 = "SELECT T.agency_type, count(*) FROM meta T WHERE T.tid in (%s)" %(curr_tid) +" GROUP BY T.agency_type"
    cur.execute(sql6)
    for row6 in cur.fetchall():
        sponsor_type = row6[0]
        percentage_sponsor_type = "%.2f" %(float(row6[1])/total_num * 100)
        distribution_sponsor_type[sponsor_type] = percentage_sponsor_type

    if "['NIH']" not in distribution_sponsor_type:
        distribution_sponsor_type["['NIH']"] = "0"
    if "['Industry']" not in distribution_sponsor_type:
        distribution_sponsor_type["['Industry']"] = "0"
    if "['U.S. Fed']" not in distribution_sponsor_type:
        distribution_sponsor_type["['U.S. Fed']"] = "0"
    if "['Other']" not in distribution_sponsor_type:
        distribution_sponsor_type["['Other']"] = "0"


    # get distribution of phase
    distribution_phase = {}
    sql7 = "SELECT T.phase, count(*) FROM meta T WHERE T.tid in (%s)" %(curr_tid) + " GROUP BY T.phase"
    cur.execute(sql7)
    for row7 in cur.fetchall():
        phase = row7[0]
        percentage_phase = "%.2f" %(float(row7[1])/total_num * 100)
        distribution_phase[phase] = percentage_phase

    if "Phase 0" not in distribution_phase:
        distribution_phase["Phase 0"] = "0"
    if "Phase 1" not in distribution_phase:
        distribution_phase["Phase 1"] = "0"
    if "Phase 2" not in distribution_phase:
        distribution_phase["Phase 2"] = "0"
    if "Phase 3" not in distribution_phase:
        distribution_phase["Phase 3"] = "0"
    if "Phase 4" not in distribution_phase:
        distribution_phase["Phase 4"] = "0"
    if "N/A" not in distribution_phase:
        distribution_phase["N/A"] = "0"

    # get distribution of gender
    distribution_gender = {}
    sql8 = "SELECT T.gender, count(*) FROM meta T WHERE T.tid in (%s)" %(curr_tid) +" GROUP BY T.gender"
    cur.execute(sql8)
    for row8 in cur.fetchall():
        gender = row8[0]
        percentage_gender = "%.2f" %(float(row8[1])/total_num * 100)
        distribution_gender[gender] = percentage_gender

    if "both" not in distribution_gender:
        distribution_gender["both"] = "0"
    if "male" not in distribution_gender:
        distribution_gender["male"] = "0"
    if "female" not in distribution_gender:
        distribution_gender["female"] = "0"

    # get distribution of intervention model
    distribution_intervention_model = {}

    sql9 = "SELECT T.intervention_model, count(*) FROM meta T WHERE T.tid in (%s)" % (curr_tid) + " GROUP BY T.intervention_model"
    cur.execute(sql9)
    for row9 in cur.fetchall():
        intervention_model = row9[0]
        percentage_intervention_model = "%.2f" %(float(row9[1])/total_num * 100)
        distribution_intervention_model[intervention_model] = percentage_intervention_model

    if "Parallel Assignment" not in distribution_intervention_model:
        distribution_intervention_model["Parallel Assignment"] = "0"
    if "Factorial Assignment" not in distribution_intervention_model:
        distribution_intervention_model["Factorial Assignment"] = "0"
    if "Crossover Assignment" not in distribution_intervention_model:
        distribution_intervention_model["Crossover Assignment"] = "0"
    if "Single Group Assignment" not in distribution_intervention_model:
        distribution_intervention_model["Single Group Assignment"] = "0"
    if "N/A" not in distribution_intervention_model:
        distribution_intervention_model["N/A"] = "0"

    # get distribution of allocation
    distribution_allocation = {}

    sql10 = "SELECT T.allocation, count(*) FROM meta T WHERE T.tid in (%s)" %(curr_tid) + " GROUP BY T.allocation"
    cur.execute(sql10)
    for row10 in cur.fetchall():
        allocation = row10[0]
        percentage_allocation = "%.2f" %(float(row10[1])/total_num * 100)
        distribution_allocation[allocation] = percentage_allocation

    if "Randomized" not in distribution_allocation:
        distribution_allocation["Randomized"] = "0"
    if "Non-Randomized" not in distribution_allocation:
        distribution_allocation["Non-Randomized"] = "0"
    if "N/A" not in distribution_allocation:
        distribution_allocation["N/A"] = "0"

    # get distribution of time perspective
    distribution_time_perspective = {}

    sql11 = "SELECT T.time_perspective, count(*) FROM meta T WHERE T.tid in (%s)" %(curr_tid) +" GROUP BY T.time_perspective"
    cur.execute(sql11)
    for row11 in cur.fetchall():
        time_perspective = row11[0]
        percentage_time_perspective = "%.2f" %(float(row11[1])/total_num * 100)
        distribution_time_perspective[time_perspective] = percentage_time_perspective

    if "Cross-Sectional" not in distribution_time_perspective:
        distribution_time_perspective["Cross-Sectional"] = "0"
    if "Non-Longitudinal" not in distribution_time_perspective:
        distribution_time_perspective["Non-Longitudinal"] = "0"
    if "Prospective" not in distribution_time_perspective:
        distribution_time_perspective["Prospective"] = "0"
    if "Retrospective" not in distribution_time_perspective:
        distribution_time_perspective["Retrospective"] = "0"
    if "N/A" not in distribution_time_perspective:
        distribution_time_perspective["N/A"] = "0"

    # generate initial value specturm
    #initial_value_spectrum, upper_value, lower_value = generate_initial_value_spectrum(cur, cui,sty, disease)

    if db.open:
        db.close()

    #return "Current disease is still %s." %disease + " Current variable is %s" %var
    return flask.render_template('query_builder.html', **locals())




@application.route('/analysis',methods=['POST','GET'])
def analysis():
    disease = flask.request.form['disease']
    cuisty = str(flask.request.form['featureInfo']).strip().split()
    cui = cuisty[0]
    sty = cuisty[1]
    name = cuisty[2]
    filter_builder = flask.request.form['filter_builder']
    db = mysql.connect()
    cur = db.cursor()

    curr_condition = "V.task = '%s' and V.cui='%s' and V.sty = '%s'"  %(disease, cui, sty)
    curr_tid = "SELECT distinct V.tid from cancer_cui where %s" %(curr_condition)

    # the list of trial IDs if the condition is not indexed in COMPACT
    trial_ids_with_conditions = []

    db = mysql.connect()
    cur = db.cursor()

    #sql = "SELECT distinct V.TID, V.month FROM cancer_cui V, meta T where %s" %(curr_condition) + " and T.tid = V.tid and "+ phase_query + " and "+ status_query + " and "+ study_type_query + " and "+ intervention_type_query + " and "+ agency_type_query + " and "+ gender_query + " and "+ start_date_query + " and "+ age_query + " and "+ intervention_model_query + " and "+ allocation_query + " and "+ time_perspective_query + " and "+ disease_query
    sql = "SELECT V.month, count(*), count(distinct V.tid) FROM cancer_cui V, meta T where %s and %s group by month order by month"  % (curr_condition, filter_builder)
    print sql

    cur.execute(sql)

    modal_boundary_output_simple = []
    modal_boundary_output_simple.append(["value", "Frequency"])
    num_of_trials = 0
    for row in cur.fetchall():
        modal_boundary_output_simple.append([str(row[0]),int(row[1])])
        num_of_trials += int(row[2])


    if (len(modal_boundary_output_simple) > 0):
        return flask.render_template('duration.html', **locals())

    return "Builder page disease %s" %disease +"; and the variable is %s" %name


@application.route('/download', methods=['POST','GET'])
def download():
    def generate():
        for row in csv_result:
            yield ','.join(row) + '\n'
            #yield ','.join(row) + '\n'
            #for index in xrange(len(row)):
            #	yield row[index]

    return flask.Response(generate(), mimetype='text/csv',headers={"Content-Disposition": "attachment;filename=VATEC_output.csv"})


def generate_initial_value_spectrum(cur, cui,sty, disease):

    trials_exps = {}
    sql = "SELECT month, count(*) from cancer_cui where cui='%s' and sty = '%s' and task = '%s' and pattern != 'None' group by month order by month" % (cui,sty,disease)
    cur.execute(sql)

    output = []
    upper_value = 0
    lower_value = 0
    output.append(["value", "Frequency"])
    for row in cur.fetchall():
        output.append([str(row[0]),int(row[1])])
        if (int(row[0])>upper_value): upper_value = int(row[0])
        if (int(row[0])<lower_value):lower_value = int(row[0])

    return (output, str(upper_value), str(lower_value))




def remove_duplicates(l):
    return list(set(l))

# get the html source associated to a URL
def download_web_data (url):
    try:
        req = urllib2.Request (url, headers={'User-Agent':"Magic Browser"})
        con = urllib2.urlopen(req)
        html = con.read()
        con.close()
        return html
    except Exception as e:
        print ('%s: %s' % (e, url))
        return None

# Find Trial IDs of a specific disease

def get_disease_clinical_trials (disease):
    # base url
    url = 'http://clinicaltrials.gov/search?cond=' + disease.replace(' ', '+') + '&displayxml=true&count='
    print("url is %s") %url
    # get the number of studies available (request 0 studies as result)
    xmltree = xml_parser.fromstring (download_web_data('%s%s' % (url, '0')))
    nnct = xmltree.get('count')
    # get the list of clinical studies
    xmltree = xml_parser.fromstring (download_web_data('%s%s' % (url, nnct)))
    lnct = xmltree.findall ('clinical_study')

    #criterias = []
    trial_ids = []

    url_trial = 'http://clinicaltrials.gov/show/%s?displayxml=true'
    for nct in lnct:
        ids = nct.find ('nct_id')
        if ids is not None:
            trial_ids.append((ids.text))
        else:
            print 'no id'

    return trial_ids



if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
