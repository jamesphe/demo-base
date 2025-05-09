import request from '@/utils/request'

// 获取用户列表
export function getUserList(params) {
  return request({
    url: '/users/search',
    method: 'get',
    params
  })
}

// 创建用户
export function createUser(data) {
  return request({
    url: '/users',
    method: 'post',
    data: {
      username: data.username,
      email: data.email,
      password: data.password,
      user_type: data.user_type,
      avatar: data.avatar,
      introduction: data.introduction,
      tenant_id: data.tenant_id,
      phone: data.phone
    }
  })
}

// 更新用户
export function updateUser(id, data) {
  return request({
    url: `/users/${id}`,
    method: 'put',
    data: {
      username: data.username,
      email: data.email,
      password: data.password,
      user_type: data.user_type,
      avatar: data.avatar,
      introduction: data.introduction,
      tenant_id: data.tenant_id,
      is_active: data.is_active,
      phone: data.phone
    }
  })
}

// 删除用户
export function deleteUser(id) {
  return request({
    url: `/users/${id}`,
    method: 'delete'
  })
}

// 更新用户角色
export function updateUserRoles(userId, roleIds) {
  // 确保转换为原生数组
  const plainRoleIds = Array.isArray(roleIds) ? roleIds.map(id => Number(id)) : []

  return request({
    url: `/users/${userId}/roles`,
    method: 'put',
    data: plainRoleIds  // 直接发送角色ID数组，不要包装在对象中
  })
}

// 获取用户角色
export function getUserRoles(userId) {
  return request({
    url: `/users/${userId}/roles`,
    method: 'get'
  })
}

// 获取所有角色列表
export function getRoleList() {
  return request({
    url: '/roles',
    method: 'get'
  })
}
