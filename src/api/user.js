import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/login/access-token',
    method: 'post',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    data: `username=${encodeURIComponent(data.username)}&password=${encodeURIComponent(data.password)}`,
    withCredentials: true
  })
}

export function getInfo() {
  return request({
    url: '/users/info',
    method: 'get'
  })
}

export function logout() {
  return request({
    url: '/vue-element-admin/user/logout',
    method: 'post'
  })
}

export function register(data) {
  return request({
    url: '/user/register',
    method: 'post',
    data
  })
}

/**
 * 申请免费试用
 * @param {Object} data - 试用申请数据
 */
export function applyForTrial(data) {
  return request({
    url: '/user/trial/apply',
    method: 'post',
    data
  })
}

/**
 * 获取试用状态
 */
export function getTrialStatus() {
  return request({
    url: '/user/trial/status',
    method: 'get'
  })
}

// 获取当前用户的权限列表
export function getUserPermissions() {
  return request({
    url: '/permissions/me',
    method: 'get'
  })
}
