#!/bin/bash

# 基础目录
BASE_DIR="src/views"

# 创建目录函数
create_view() {
    local path=$1
    local name=$2
    mkdir -p "${BASE_DIR}/${path}"
    cat > "${BASE_DIR}/${path}/index.vue" << EOF
<template>
  <div class="app-container">
    <h2>${name}</h2>
  </div>
</template>

<script>
export default {
  name: '${name}'
}
</script>
EOF
}

# HRMS 相关视图
mkdir -p "${BASE_DIR}/hrms/basic"
mkdir -p "${BASE_DIR}/hrms/labor"
mkdir -p "${BASE_DIR}/hrms/salary"
mkdir -p "${BASE_DIR}/hrms/training"
mkdir -p "${BASE_DIR}/hrms/assessment"

# 创建基础信息维护相关视图
create_view "hrms/basic" "Basic"
create_view "hrms/basic/organization" "Organization"
create_view "hrms/basic/position" "Position"
create_view "hrms/basic/title" "Title"
create_view "hrms/basic/staff" "Staff"

# 创建劳动关系维护相关视图
create_view "hrms/labor" "Labor"
create_view "hrms/labor/entry" "Entry"
create_view "hrms/labor/contract" "Contract"
create_view "hrms/labor/certificate" "Certificate"

# 创建薪酬维护相关视图
create_view "hrms/salary" "Salary"
create_view "hrms/salary/base" "SalaryBase"
create_view "hrms/salary/course" "SalaryCourse"
create_view "hrms/salary/hr" "SalaryHR"

# 创建培训维护相关视图
create_view "hrms/training" "Training"
create_view "hrms/training/plan" "TrainingPlan"
create_view "hrms/training/sign" "TrainingSign"
create_view "hrms/training/feedback" "TrainingFeedback"

# 创建考核维护相关视图
create_view "hrms/assessment" "Assessment"
create_view "hrms/assessment/hr" "AssessmentHR"
create_view "hrms/assessment/course" "AssessmentCourse"

# 创建招聘管理相关视图
mkdir -p "${BASE_DIR}/recruitment"
create_view "recruitment/plan" "RecruitmentPlan"
create_view "recruitment/post" "RecruitmentPost"

# 创建劳动关系管理相关视图
mkdir -p "${BASE_DIR}/labor"
create_view "labor/entry" "LaborEntry"
create_view "labor/contract" "LaborContract"
create_view "labor/retire" "LaborRetire"

# 创建薪资管理相关视图
mkdir -p "${BASE_DIR}/salary"
create_view "salary/setting" "SalarySetting"
create_view "salary/base" "SalaryBase"
create_view "salary/course" "SalaryCourse"
create_view "salary/hr" "SalaryHR"
create_view "salary/payment" "SalaryPayment"
create_view "salary/report" "SalaryReport"

# 创建其他模块的基础视图
mkdir -p "${BASE_DIR}/attendance"
create_view "attendance" "Attendance"

mkdir -p "${BASE_DIR}/evaluation"
create_view "evaluation" "Evaluation"

mkdir -p "${BASE_DIR}/system"
create_view "system" "System"

mkdir -p "${BASE_DIR}/transfer"
create_view "transfer" "Transfer"

# 创建考勤管理相关视图
mkdir -p "${BASE_DIR}/attendance/leave"
create_view "attendance/leave" "Leave"
create_view "attendance/leave/apply" "LeaveApply"
create_view "attendance/leave/approve" "LeaveApprove"
create_view "attendance/leave/query" "LeaveQuery"

mkdir -p "${BASE_DIR}/attendance/check"
create_view "attendance/check" "Check"
create_view "attendance/check/sign" "CheckSign"
create_view "attendance/check/appeal" "CheckAppeal"
create_view "attendance/check/report" "CheckReport"

# 创建教职工考核相关视图
mkdir -p "${BASE_DIR}/evaluation"
create_view "evaluation/setting" "EvaluationSetting"
create_view "evaluation/record" "EvaluationRecord"
create_view "evaluation/query" "EvaluationQuery"

# 创建系统设置相关视图
mkdir -p "${BASE_DIR}/system"
create_view "system/user" "User"
create_view "system/role" "Role"
create_view "system/api" "Api"
create_view "system/log" "Log"
create_view "system/param" "Param"
create_view "system/backup" "Backup"

# 创建人事调动相关视图
mkdir -p "${BASE_DIR}/transfer"
create_view "transfer/apply" "TransferApply"
create_view "transfer/approve" "TransferApprove"
create_view "transfer/order" "TransferOrder"
create_view "transfer/confirm" "TransferConfirm"

# 创建社保管理相关视图
mkdir -p "${BASE_DIR}/social"
create_view "social/base" "SocialBase"
create_view "social/info" "SocialInfo"
create_view "social/change" "SocialChange"
create_view "social/transfer" "SocialTransfer"
create_view "social/staff" "SocialStaff"
create_view "social/statistics" "SocialStatistics"
create_view "social/course" "SocialCourse" 