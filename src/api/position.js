import request from '@/utils/request'

// 获取职位列表
export function getPositionList(params) {
  return request({
    url: '/position/list',
    method: 'get',
    params
  })
}

// 发布职位
export function publishPosition(data) {
  return request({
    url: '/position/publish',
    method: 'post',
    data
  })
}

// 更新职位
export function updatePosition(data) {
  return request({
    url: `/position/${data.id}`,
    method: 'put',
    data
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

// 删除职位
export function deletePosition(id) {
  return request({
    url: `/position/${id}`,
    method: 'delete'
  })
} 