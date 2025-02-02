import request from '@/utils/request'

// 获取实训基地列表
export function getBaseList() {
  return request({
    url: '/base/list',
    method: 'get'
  })
}

// 添加实训基地
export function addBase(data) {
  return request({
    url: '/base',
    method: 'post',
    data
  })
}

// 更新实训基地
export function updateBase(data) {
  return request({
    url: `/base/${data.id}`,
    method: 'put',
    data
  })
}

// 删除实训基地
export function deleteBase(id) {
  return request({
    url: `/base/${id}`,
    method: 'delete'
  })
} 