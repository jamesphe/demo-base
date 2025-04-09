import request from '@/utils/request'

// 获取试用申请列表
export function getTrialList(params) {
  return request({
    url: '/trial/list',
    method: 'get',
    params
  })
}

// 审批通过试用申请
export function approveTrial(id, data) {
  return request({
    url: `/trial/${id}/approve`,
    method: 'put',
    data
  })
}

// 拒绝试用申请
export function rejectTrialApplication(id, reason) {
  return request({
    url: `/trial/${id}/reject`,
    method: 'put',
    data: { reason }
  })
}

// 更新试用状态
export function updateTrialStatus(id, status) {
  return request({
    url: `/trial/${id}/status`,
    method: 'put',
    data: { status }
  })
}

// 编辑试用信息
export function updateTrial(id, data) {
  return request({
    url: `/trial/${id}`,
    method: 'put',
    data
  })
}

// 获取所有试用申请记录
export function getAllTrialList(params) {
  return request({
    url: '/trial/list',
    method: 'get',
    params
  })
}

export function getPendingTrials(params) {
  return request({
    url: '/trial/pending',
    method: 'get',
    params
  })
}

export function rejectTrial(id, data) {
  return request({
    url: `/trial/${id}/reject`,
    method: 'put',
    data
  })
}
