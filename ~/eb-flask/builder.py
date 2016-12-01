__author__ = 'Jason'
import os, re, csv, ast, csv
import math
import jinja2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
import flask

def _build_query(mysql):
    var, aggregator_output, minimum_value, maximum_value, lower, upper, value_range_verification_output, enrollment_value, value_spectrum_output, num_trials, phase_query, condition_query, query_used, phases, conditions, status_query, statuses, study_type_query, study_types, intervention_type_query, intervention_types, agency_type_query, agency_types, gender_query, gender, modal_boundary_output, enrollment_spectrum_output, num_of_trials_output, detail_enrollment_spectrum_output,value_spectrum_output_trial_ids, initial_value_spectrum, on_option_page, start_date_query, start_date, age_query, value_range_distribution_output,value_range_width_distribution_output, average_enrollment_spectrum_output, disease, intervention_model_query, allocation_query, intervention_models, allocations, time_perspective_query, time_perspectives, start_date_before = '', "", '', '', '', '', '', '', "", [], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', "", "", "", "", "", "", '', '', '', '', "", "", "", '', '','','','','','',''

    disease = flask.request.form['disease']
    typed_disease = flask.request.form.get('typed_disease','')
    if(disease == '' and typed_disease !=''):
        disease = typed_disease

    db = mysql.connect()
    cur = db.cursor()

    sql_var = [disease]
    curr_condition = "task = %s"
    curr_tid = "SELECT distinct tid from cancer_cui where %s" %(curr_condition)
    # get number of trials of the selected disease
    sql1 = "SELECT count(cui), count(distinct tid) FROM cancer_cui where %s " %(curr_condition)
    cur.execute(sql1, sql_var)
    total_num_cui = 0
    total_num_tid = 0
    for row in cur.fetchall():
        total_num_cui = int(row[0])
        total_num_tid = int(row[1])
        aggregator_output += "There are <span style=color:red>%s</span>  UMLS terms (may repeat) and %s clinical trails for condition <span style=color:red>%s</span> <br><br>" % (total_num_cui,total_num_tid,disease)

    # get distribution of study types
    distribution_study_type = {}
    sql3 = "SELECT T.study_type, count(distinct T.tid) FROM meta T WHERE T.tid in (SELECT tid from cancer_cui where %s)" %(curr_condition)  + " GROUP BY T.study_type"
    cur.execute(sql3, sql_var)
    for row3 in cur.fetchall():
        study_type = row3[0]
        percentage_study_type = "%.2f" %(float(row3[1])/total_num_tid * 100)
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
    cur.execute(sql4_all,sql_var)
    for row4_all in cur.fetchall():
        num_trials_with_intervention_type = int(row4_all[0])

    sql4 = "SELECT T.intervention_type, count(distinct T.tid) FROM meta T WHERE T.tid in (%s)" %(curr_tid) +" GROUP BY T.intervention_type"
    cur.execute(sql4,sql_var)
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
    sql5 = "SELECT T.overall_status, count(distinct T.tid) FROM meta T WHERE T.tid in (%s)" %(curr_tid) + " GROUP BY T.overall_status"
    cur.execute(sql5,sql_var)
    for row5 in cur.fetchall():
        status = row5[0]
        percentage_status = "%.2f" %(float(row5[1])/total_num_tid * 100)
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
    sql6 = "SELECT T.agency_type, count(distinct T.tid) FROM meta T WHERE T.tid in (%s)" %(curr_tid) +" GROUP BY T.agency_type"
    cur.execute(sql6, sql_var)
    for row6 in cur.fetchall():
        sponsor_type = row6[0]
        percentage_sponsor_type = "%.2f" %(float(row6[1])/total_num_tid * 100)
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
    sql7 = "SELECT T.phase, count(distinct T.tid) FROM meta T WHERE T.tid in (%s)" %(curr_tid) + " GROUP BY T.phase"
    cur.execute(sql7, sql_var)
    for row7 in cur.fetchall():
        phase = row7[0]
        percentage_phase = "%.2f" %(float(row7[1])/total_num_tid * 100)
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
    sql8 = "SELECT T.gender, count(distinct T.tid) FROM meta T WHERE T.tid in (%s)" %(curr_tid) +" GROUP BY T.gender"
    cur.execute(sql8, sql_var)
    for row8 in cur.fetchall():
        gender = row8[0]
        percentage_gender = "%.2f" %(float(row8[1])/total_num_tid * 100)
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
    cur.execute(sql9, sql_var)
    for row9 in cur.fetchall():
        intervention_model = row9[0]
        percentage_intervention_model = "%.2f" %(float(row9[1])/total_num_tid * 100)
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

    sql10 = "SELECT T.allocation, count(distinct T.tid) FROM meta T WHERE T.tid in (%s)" %(curr_tid) + " GROUP BY T.allocation"
    cur.execute(sql10, sql_var)
    for row10 in cur.fetchall():
        allocation = row10[0]
        percentage_allocation = "%.2f" %(float(row10[1])/total_num_tid * 100)
        distribution_allocation[allocation] = percentage_allocation

    if "Randomized" not in distribution_allocation:
        distribution_allocation["Randomized"] = "0"
    if "Non-Randomized" not in distribution_allocation:
        distribution_allocation["Non-Randomized"] = "0"
    if "N/A" not in distribution_allocation:
        distribution_allocation["N/A"] = "0"

    # get distribution of time perspective
    distribution_time_perspective = {}

    sql11 = "SELECT T.time_perspective, count(distinct T.tid) FROM meta T WHERE T.tid in (%s)" %(curr_tid) +" GROUP BY T.time_perspective"
    cur.execute(sql11, sql_var)
    for row11 in cur.fetchall():
        time_perspective = row11[0]
        percentage_time_perspective = "%.2f" %(float(row11[1])/total_num_tid * 100)
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

    # get pattern list
    distribution_time_pattern = []
    sql12 = "SELECT V.pattern, count(*) as freq FROM cancer_cui V WHERE %s" %(curr_condition) +" GROUP BY V.pattern order by freq desc"
    cur.execute(sql12, sql_var)
    for row11 in cur.fetchall():
        pt = row11[0]
        percentage_pattern = "%.2f" %(float(row11[1])/total_num_cui * 100)
        distribution_time_pattern.append((pt,percentage_pattern))

    # generate initial value specturm
    #initial_value_spectrum, upper_value, lower_value = generate_initial_value_spectrum(cur, cui,sty, disease)

    if db.open:
        db.close()
    #return "Current disease is still %s." %disease + " Current variable is %s" %var
    return flask.render_template('query_builder.html', **locals())


def generate_initial_value_spectrum(cur, cui,sty, disease):

    trials_exps = {}
    sql_var = [cui,sty,disease]
    sql = "SELECT month, count(*) from cancer_cui where cui=%s and sty = %s and task = %s and pattern != 'None' group by month order by month"
    cur.execute(sql,sql_var)

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



