import request from '@/utils/request'

// 获取租户列表
export function getTenantList(params) {
  return request({
    url: '/tenants',
    method: 'get',
    params
  })
}

// 创建租户
export function createTenant(data) {
  return request({
    url: '/tenants',
    method: 'post',
    data
  })
}

// 更新租户
export function updateTenant(id, data) {
  return request({
    url: `/tenants/${id}`,
    method: 'put',
    data
  })
}

// 删除租户
export function deleteTenant(id) {
  return request({
    url: `/tenants/${id}`,
    method: 'delete'
  })
}

// 获取租户详情
export function getTenantDetail(id) {
  return request({
    url: `/tenants/${id}`,
    method: 'get'
  })
}
