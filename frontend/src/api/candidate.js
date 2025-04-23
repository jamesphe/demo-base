import request from '@/utils/request'

// 获取候选人列表
export function getCandidateList(params) {
  return request({
    url: '/candidate/list',
    method: 'get',
    params
  })
}

// 创建候选人
export function createCandidate(data) {
  return request({
    url: '/candidate/create',
    method: 'post',
    data
  })
}

// 更新候选人
export function updateCandidate(data) {
  return request({
    url: `/candidate/update/${data.id}`,
    method: 'put',
    data
  })
}

// 删除候选人
export function deleteCandidate(id) {
  return request({
    url: `/candidate/delete/${id}`,
    method: 'delete'
  })
}

// 更新候选人状态
export function updateCandidateStatus(id, data) {
  return request({
    url: `/candidate/${id}/status`,
    method: 'put',
    data
  })
}

// 获取候选人详情
export function getCandidateDetail(id) {
  return request({
    url: `/candidate/${id}`,
    method: 'get'
  })
}

// 获取评估列表
export function getEvaluationList(params) {
  return request({
    url: '/candidate/evaluation/list',
    method: 'get',
    params
  })
}

// 获取职位列表
export function getPositionList(query) {
  return request({
    url: '/position/list',
    method: 'get',
    params: query
  })
}

// 获取推荐候选人列表
export function getRecommendations(query) {
  return request({
    url: '/candidate/recommendation/list',
    method: 'get',
    params: query
  })
}

// 获取评估详情
export function getEvaluationDetail(id) {
  return request({
    url: '/candidate/evaluation/detail',
    method: 'get',
    params: { id }
  })
}

// 提交评估
export function createEvaluation(data) {
  return request({
    url: '/candidate/evaluation/create',
    method: 'post',
    data
  })
}

// 获取推荐候选人详情
export function getRecommendationDetail(id) {
  return request({
    url: '/candidate/recommendation/detail',
    method: 'get',
    params: { id }
  })
}

// 联系候选人
export function contactCandidate(data) {
  return request({
    url: '/candidate/recommendation/contact',
    method: 'post',
    data
  })
}
