import request from '@/utils/request'

// 获取院系列表
export function getDepartmentList(query) {
  return request({
    url: '/department/list',
    method: 'get',
    params: query
  })
}

// 添加院系
export function addDepartment(data) {
  return request({
    url: '/department',
    method: 'post',
    data
  })
}

// 更新院系
export function updateDepartment(data) {
  return request({
    url: `/department/${data.id}`,
    method: 'put',
    data
  })
}

// 删除院系
export function deleteDepartment(id) {
  return request({
    url: `/department/${id}`,
    method: 'delete'
  })
} 