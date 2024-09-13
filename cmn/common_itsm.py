# payload는 config로 작성하고자 했으나, xml의 경우 선언할때 바로 매개변수를 받아서 작성해야하기 때문에 common의 함수로 사용
def get_itsm_payload(ITSM_OFFSET_SIZE, ITSM_MAX_CNT_SIZE, ITSM_SRCH_ST_DATE, ITSM_SRCH_END_DATE, SEARCH_CL_CD):
    payload = f'<?xml version="1.0" encoding="UTF-8"?> \
    <Root xmlns="http://www.nexacroplatform.com/platform/dataset"> \
        <Parameters> \
            <Parameter id="offset">{ITSM_OFFSET_SIZE}</Parameter> \
            <Parameter id="max_cnt">{ITSM_MAX_CNT_SIZE}</Parameter> \
        </Parameters> \
        <Dataset id="paramVO"> \
            <ColumnInfo> \
                <Column id="codeTypeId" type="STRING" size="256" /> \
                <Column id="startDate" type="STRING" size="256" /> \
                <Column id="endDate" type="STRING" size="256" /> \
                <Column id="searchDiv1" type="STRING" size="256" /> \
                <Column id="searchDiv2" type="STRING" size="256" /> \
                <Column id="searchValue1" type="STRING" size="256" /> \
                <Column id="searchValue2" type="STRING" size="256" /> \
                <Column id="searchValue3" type="STRING" size="256" /> \
                <Column id="searchValue4" type="STRING" size="256" /> \
                <Column id="searchValue5" type="STRING" size="256" /> \
                <Column id="div_id" type="STRING" size="256" /> \
                <Column id="workflow_id" type="STRING" size="256" /> \
                <Column id="searchValue6" type="STRING" size="256" /> \
                <Column id="searchValue7" type="STRING" size="256" /> \
                <Column id="searchValue8" type="STRING" size="256" /> \
                <Column id="searchValue9" type="STRING" size="256" /> \
                <Column id="searchValue10" type="STRING" size="256" /> \
                <Column id="label_1" type="STRING" size="256" /> \
                <Column id="label_2" type="STRING" size="256" /> \
                <Column id="label_3" type="STRING" size="256" /> \
                <Column id="label_4" type="STRING" size="256" /> \
                <Column id="label_5" type="STRING" size="256" /> \
                <Column id="label_6" type="STRING" size="256" /> \
                <Column id="label_7" type="STRING" size="256" /> \
                <Column id="label_8" type="STRING" size="256" /> \
                <Column id="label_9" type="STRING" size="256" /> \
                <Column id="user_id" type="STRING" size="256" /> \
                <Column id="request_id" type="STRING" size="256" /> \
                <Column id="process_id" type="STRING" size="256" /> \
                <Column id="label_10" type="STRING" size="256" /> \
                <Column id="csr_type_code" type="STRING" size="256" /> \
                <Column id="sub_csr_type_code" type="STRING" size="256" /> \
                <Column id="auth_group_id" type="STRING" size="256" /> \
                <Column id="code_type_id" type="STRING" size="256" /> \
                <Column id="parent_code_id" type="STRING" size="256" /> \
                <Column id="user_name" type="STRING" size="256" /> \
                <Column id="dept_name" type="STRING" size="256" /> \
                <Column id="company_name" type="STRING" size="256" /> \
                <Column id="dept_id" type="STRING" size="256" /> \
                <Column id="category_id" type="STRING" size="256" /> \
                <Column id="combo_search" type="STRING" size="256" /> \
                <Column id="edt_input" type="STRING" size="256" /> \
                <Column id="faq_id" type="STRING" size="256" /> \
                <Column id="title" type="STRING" size="256" /> \
                <Column id="reg_user_id" type="STRING" size="256" /> \
                <Column id="content" type="STRING" size="256" /> \
                <Column id="notice_id" type="STRING" size="256" /> \
                <Column id="code_type_name" type="STRING" size="256" /> \
                <Column id="ci_type_id" type="STRING" size="256" /> \
                <Column id="col_id" type="STRING" size="256" /> \
                <Column id="worker_user_id" type="STRING" size="256" /> \
                <Column id="cn_id" type="STRING" size="256" /> \
                <Column id="is_code" type="STRING" size="256" /> \
                <Column id="auth_id" type="STRING" size="256" /> \
                <Column id="category_type_code" type="STRING" size="256" /> \
                <Column id="category_level" type="STRING" size="256" /> \
                <Column id="work_seq_no" type="STRING" size="256" /> \
                <Column id="start_date" type="STRING" size="256" /> \
                <Column id="end_date" type="STRING" size="256" /> \
                <Column id="search_type" type="STRING" size="256" /> \
                <Column id="search_text" type="STRING" size="256" /> \
                <Column id="request_user_div_id" type="STRING" size="256" /> \
                <Column id="trouble_level_code" type="STRING" size="256" /> \
                <Column id="trouble_manage_type_code" type="STRING" size="256" /> \
                <Column id="trouble_treat_result_code" type="STRING" size="256" /> \
                <Column id="flag" type="STRING" size="256" /> \
                <Column id="is_finish" type="STRING" size="256" /> \
                <Column id="if_flag" type="STRING" size="256" /> \
                <Column id="is_active" type="STRING" size="256" /> \
                <Column id="csr_type_gubun_code" type="STRING" size="256" /> \
                <Column id="csr_type_basis_code" type="STRING" size="256" /> \
                <Column id="reg_time" type="STRING" size="256" /> \
                <Column id="is_mail_rcv" type="STRING" size="256" /> \
                <Column id="user_pwd" type="STRING" size="256" /> \
                <Column id="now_pwd" type="STRING" size="256" /> \
                <Column id="input_pwd" type="STRING" size="256" /> \
                <Column id="is_sms_rcv" type="STRING" size="256" /> \
                <Column id="batch_id" type="STRING" size="256" /> \
                <Column id="batch_name" type="STRING" size="256" /> \
                <Column id="is_used" type="STRING" size="256" /> \
                <Column id="first_reg_user_id" type="STRING" size="256" /> \
                <Column id="first_reg_time" type="STRING" size="256" /> \
                <Column id="last_mod_user_id" type="STRING" size="256" /> \
                <Column id="last_mod_time" type="STRING" size="256" /> \
                <Column id="exec_status" type="STRING" size="256" /> \
                <Column id="is_team_yn" type="STRING" size="256" /> \
                <Column id="process_status_code" type="STRING" size="256" /> \
                <Column id="trt_user_id" type="STRING" size="256" /> \
                <Column id="is_code_name" type="STRING" size="256" /> \
                <Column id="is_type_code" type="STRING" size="256" /> \
                <Column id="status_type" type="STRING" size="256" /> \
                <Column id="manager_flag" type="STRING" size="256" /> \
                <Column id="list_type" type="STRING" size="256" /> \
                <Column id="service_level_code" type="STRING" size="256" /> \
                <Column id="trouble_minute" type="INT" size="256" /> \
                <Column id="check_yn" type="STRING" size="256" /> \
                <Column id="service_catalog_code" type="STRING" size="256" /> \
                <Column id="notice_target_list" type="STRING" size="256" /> \
                <Column id="user_language" type="STRING" size="256" /> \
                <Column id="function_name" type="STRING" size="256" /> \
                <Column id="procedure_name" type="STRING" size="256" /> \
                <Column id="slm_gubun" type="STRING" size="256" /> \
                <Column id="search_gubun" type="STRING" size="256" /> \
                <Column id="date_gubun" type="STRING" size="256" /> \
                <Column id="category_column_name" type="STRING" size="256" /> \
                <Column id="category_parent_id" type="STRING" size="256" /> \
                <Column id="start_yyyymm" type="STRING" size="256" /> \
                <Column id="end_yyyymm" type="STRING" size="256" /> \
                <Column id="perform_mgnt_reading_yn" type="STRING" size="256" /> \
                <Column id="process_code" type="STRING" size="256" /> \
                <Column id="req_type_code" type="STRING" size="256" /> \
                <Column id="problem_type_code" type="STRING" size="256" /> \
                <Column id="problem_type_basis_code" type="STRING" size="256" /> \
                <Column id="sub_problem_type_code" type="STRING" size="256" /> \
                <Column id="problem_type_gubun_code" type="STRING" size="256" /> \
                <Column id="str_div_info" type="STRING" size="256" /> \
                <Column id="am_cate_id" type="STRING" size="256" /> \
                <Column id="am_attr_id" type="STRING" size="256" /> \
                <Column id="am_div_id" type="STRING" size="256" /> \
                <Column id="curr_am_attr_id" type="STRING" size="256" /> \
                <Column id="curr_am_col_order" type="STRING" size="256" /> \
                <Column id="ch_am_attr_id" type="STRING" size="256" /> \
                <Column id="ch_am_col_order" type="STRING" size="256" /> \
                <Column id="ap_div_id" type="STRING" size="256" /> \
                <Column id="ap_cate_id" type="STRING" size="256" /> \
                <Column id="ap_asset_id" type="STRING" size="256" /> \
                <Column id="am_parent_cate_id" type="STRING" size="256" /> \
                <Column id="user_div_id" type="STRING" size="256" /> \
                <Column id="charge_yyyymm" type="STRING" size="256" /> \
                <Column id="charge_dept_code" type="STRING" size="256" /> \
                <Column id="last_year" type="STRING" size="256" /> \
                <Column id="work_yyyymm" type="STRING" size="256" /> \
                <Column id="year" type="STRING" size="256" /> \
                <Column id="charge_yn" type="STRING" size="256" /> \
                <Column id="charge_grade_code" type="STRING" size="256" /> \
                <Column id="pre_month" type="STRING" size="256" /> \
                <Column id="charge_div_id" type="STRING" size="256" /> \
                <Column id="change_desc" type="STRING" size="256" /> \
                <Column id="this_month" type="STRING" size="256" /> \
                <Column id="old_chargeDeptCode" type="STRING" size="256" /> \
                <Column id="charge_price" type="STRING" size="256" /> \
                <Column id="satisfaction_score" type="STRING" size="256" /> \
                <Column id="satisfaction_score_5" type="STRING" size="256" /> \
                <Column id="satisfaction_score_4" type="STRING" size="256" /> \
                <Column id="satisfaction_score_3" type="STRING" size="256" /> \
                <Column id="satisfaction_score_2" type="STRING" size="256" /> \
                <Column id="satisfaction_score_1" type="STRING" size="256" /> \
                <Column id="last_month" type="STRING" size="256" /> \
                <Column id="as_cate_id" type="STRING" size="256" /> \
                <Column id="as_asset_id" type="STRING" size="256" /> \
                <Column id="appr_id" type="STRING" size="256" /> \
                <Column id="appr_gubun_code" type="STRING" size="256" /> \
                <Column id="belong_to_nation" type="STRING" size="256" /> \
                <Column id="code_use_yn_guam" type="STRING" size="256" /> \
                <Column id="code_use_yn_thailand" type="STRING" size="256" /> \
                <Column id="code_use_yn_indonesia" type="STRING" size="256" /> \
                <Column id="code_use_yn_japan" type="STRING" size="256" /> \
                <Column id="conf_appr_status_code" type="STRING" size="256" /> \
                <Column id="close_appr_status_code" type="STRING" size="256" /> \
                <Column id="tax_bill_submit_yn" type="STRING" size="256" /> \
                <Column id="sort_gubun_code" type="STRING" size="256" /> \
                <Column id="sub_dept_id" type="STRING" size="256" /> \
                <Column id="sub_dept_display_yn" type="STRING" size="256" /> \
                <Column id="code_use_yn_vietnam" type="STRING" size="256" /> \
                <Column id="ma_div_id" type="STRING" size="256" /> \
                <Column id="is_maintenance_yn" type="STRING" size="256" /> \
                <Column id="con_year" type="STRING" size="256" /> \
                <Column id="con_id" type="STRING" size="256" /> \
                <Column id="mtn_item_id" type="STRING" size="256" /> \
                <Column id="det_item_id" type="STRING" size="256" /> \
                <Column id="pos_con_yn" type="STRING" size="256" /> \
                <Column id="is_confirm" type="STRING" size="256" /> \
                <Column id="is_talk_rcv" type="STRING" size="256" /> \
                <Column id="is_widget_rcv" type="STRING" size="256" /> \
                <Column id="is_portlet_fold_yn" type="STRING" size="256" /> \
                <Column id="confirmYn" type="STRING" size="256" /> \
                <Column id="ldcc_user_id" type="STRING" size="256" /> \
                <Column id="divide_csr" type="STRING" size="256" /> \
                <Column id="is_auto_confirm_line" type="STRING" size="256" /> \
                <Column id="trouble_id" type="STRING" size="256" /> \
                <Column id="excel_count" type="STRING" size="256" /> \
                <Column id="step_code" type="STRING" size="256" /> \
            </ColumnInfo> \
            <Rows> \
                <Row> \
                    <Col id="searchValue1">Yes</Col> \
                    <Col id="searchValue2">No</Col> \
                    <Col id="searchValue3">No</Col> \
                    <Col id="searchValue4">No</Col> \
                    <Col id="searchValue5">No</Col> \
                    <Col id="div_id">023400</Col> \
                    <Col id="searchValue6">No</Col> \
                    <Col id="searchValue7">No</Col> \
                    <Col id="searchValue8">No</Col> \
                    <Col id="searchValue9">No</Col> \
                    <Col id="searchValue10">No</Col> \
                    <Col id="label_1" /> \
                    <Col id="label_2" /> \
                    <Col id="label_10">No</Col> \
                    <Col id="csr_type_code" /> \
                    <Col id="sub_csr_type_code" /> \
                    <Col id="is_code">020</Col> \
                    <Col id="start_date">{ITSM_SRCH_ST_DATE}</Col> \
                    <Col id="end_date">{ITSM_SRCH_END_DATE}</Col> \
                    <Col id="search_type">01</Col> \
                    <Col id="user_language">kr</Col> \
                    <Col id="search_gubun">{SEARCH_CL_CD}</Col> \
                    <Col id="date_gubun">01</Col> \
                    <Col id="divide_csr">No</Col> \
                </Row> \
            </Rows> \
        </Dataset> \
    </Root> \
    '
    return payload
