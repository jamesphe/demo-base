import request from '@/utils/request'

export function fetchList(query) {
  return request({
    url: '/dev-api/vue-element-admin/title/list',
    method: 'get',
    params: query
  })
}

export function createTitle(data) {
  return request({
    url: '/dev-api/vue-element-admin/title/create',
    method: 'post',
    data
  })
}

export function updateTitle(data) {
  return request({
    url: '/dev-api/vue-element-admin/title/update',
    method: 'post',
    data
  })
}
