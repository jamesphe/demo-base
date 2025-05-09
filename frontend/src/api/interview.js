import request from '@/utils/request'

// 创建面试
export function createInterview(data) {
  return request({
    url: '/interviews',
    method: 'post',
    data
  })
}

// 获取面试列表
export function getInterviewList(params) {
  return request({
    url: '/interviews',
    method: 'get',
    params
  })
}

// 获取面试详情
export function getInterviewDetail(id) {
  return request({
    url: `/interviews/${id}`,
    method: 'get'
  })
}

// 更新面试信息
export function updateInterview(id, data) {
  return request({
    url: `/interviews/${id}`,
    method: 'put',
    data
  })
}

// 删除面试
export function deleteInterview(id) {
  return request({
    url: `/interviews/${id}`,
    method: 'delete'
  })
}

// 检查面试时间冲突
export function checkTimeConflict(data) {
  return request({
    url: '/interviews/check-time-conflict',
    method: 'post',
    data
  })
}

// 获取面试官列表
export function getInterviewerList() {
  return request({
    url: '/interviews/interviewers',
    method: 'get'
  })
}

// 提交面试评估
export function submitInterviewEvaluation(id, data) {
  return request({
    url: `/interviews/${id}/evaluation`,
    method: 'post',
    data
  })
}

// 获取面试评估详情
export function getInterviewEvaluation(id) {
  return request({
    url: `/interviews/${id}/evaluation`,
    method: 'get'
  })
}

// 获取面试准备材料
export function getInterviewPreparation(interviewId) {
  return request({
    url: `/interviews/${interviewId}/preparation`,
    method: 'get'
  })
}

// 生成面试准备材料
export function generateInterviewPreparation(interviewId, data) {
  return request({
    url: `/interviews/${interviewId}/preparation/generate`,
    method: 'post',
    data
  })
}

// 更新面试准备材料
export function updateInterviewPreparation(interviewId, data) {
  return request({
    url: `/interviews/${interviewId}/preparation`,
    method: 'put',
    data
  })
}

// 获取面试官关注点
export function getInterviewerFocusPoints() {
  return request({
    url: '/interviewers/focus-points',
    method: 'get'
  })
}

// 保存面试官关注点
export function saveInterviewerFocusPoints(data) {
  return request({
    url: '/interviewers/focus-points',
    method: 'post',
    data
  })
} 