import request from '@/utils/request'

export function getPermissions(params) {
  return request({
    url: '/permissions',
    method: 'get',
    params
  })
}

export function createPermission(data) {
  return request({
    url: '/permissions',
    method: 'post',
    data
  })
}

export function updatePermission(id, data) {
  return request({
    url: `/permissions/${id}`,
    method: 'put',
    data
  })
}

export function deletePermission(id) {
  return request({
    url: `/permissions/${id}`,
    method: 'delete'
  })
}

export function getUserPermissions() {
  return request({
    url: '/permissions/me',
    method: 'get'
  })
}

export function getRolePermissions(roleId) {
  return request({
    url: `/roles/${roleId}/permissions`,
    method: 'get'
  })
}
