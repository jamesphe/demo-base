import request from '@/utils/request'

// 获取候选人列表
export function getCandidateList(params) {
  return request({
    url: '/vue-element-admin/candidate/list',
    method: 'get',
    params
  })
}

// 获取评估列表
export function getEvaluationList(params) {
  return request({
    url: '/vue-element-admin/candidate/evaluation/list',
    method: 'get',
    params
  })
}

// 获取职位列表
export function getPositionList(params) {
  return request({
    url: '/vue-element-admin/position/list',
    method: 'get',
    params
  })
}

// 获取推荐候选人列表
export function getRecommendations(params) {
  return request({
    url: '/vue-element-admin/candidate/recommendation',
    method: 'get',
    params
  })
}

// 获取评估详情
export function getEvaluationDetail(id) {
  return request({
    url: '/dev-api/vue-element-admin/candidate/evaluation/detail',
    method: 'get',
    params: { id }
  })
}

// 提交评估
export function createEvaluation(data) {
  return request({
    url: '/dev-api/vue-element-admin/candidate/evaluation/create',
    method: 'post',
    data
  })
}

// 获取推荐候选人详情
export function getRecommendationDetail(id) {
  return request({
    url: '/dev-api/vue-element-admin/candidate/recommendation/detail',
    method: 'get',
    params: { id }
  })
}

// 联系候选人
export function contactCandidate(data) {
  return request({
    url: '/dev-api/vue-element-admin/candidate/recommendation/contact',
    method: 'post',
    data
  })
} 