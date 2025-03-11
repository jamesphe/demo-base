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
