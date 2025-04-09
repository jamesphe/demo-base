import request from '@/utils/request'

// 获取职位列表
export function getPositionList(params) {
  return request({
    url: '/jobs',
    method: 'get',
    params
  })
}

// 创建职位
export function createPosition(data) {
  return request({
    url: '/jobs',
    method: 'post',
    data
  })
}

// 更新职位
export function updatePosition(id, data) {
  return request({
    url: `/jobs/${id}`,
    method: 'put',
    data
  })
}

// 删除职位
export function deletePosition(id) {
  return request({
    url: `/jobs/${id}`,
    method: 'delete'
  })
}

// 发布职位
export function publishPosition(data) {
  return request({
    url: '/jobs',
    method: 'post',
    data
  })
}

// 获取职位详情
export function getPositionDetail(id) {
  return request({
    url: `/jobs/${id}`,
    method: 'get'
  })
}

// 更新职位状态
export function updatePositionStatus(id, status) {
  return request({
    url: `/position/${id}/status`,
    method: 'put',
    data: { status }
  })
}
