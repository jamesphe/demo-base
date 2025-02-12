import request from '@/utils/request'

export function getApplyList(query) {
  console.log('API request query:', query)
  return request({
    url: '/consumable/apply/list',
    method: 'get',
    params: query
  })
}

export function createApply(data) {
  return request({
    url: '/consumable/apply/create',
    method: 'post',
    data
  })
}

export function updateApplyStatus(id, status) {
  return request({
    url: `/consumable/apply/${id}/status`,
    method: 'put',
    data: { status }
  })
} 