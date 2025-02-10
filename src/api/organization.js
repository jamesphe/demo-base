import request from '@/utils/request'

// 获取部门列表
export function getDeptList() {
  return request({
    url: '/vue-element-admin/department/list',
    method: 'get'
  })
}

// 新增部门
export function addDept(data) {
  return request({
    url: '/vue-element-admin/department',
    method: 'post',
    data
  })
}

// 更新部门
export function updateDept(data) {
  return request({
    url: '/vue-element-admin/department',
    method: 'put',
    data
  })
}

// 删除部门
export function deleteDept(id) {
  return request({
    url: `/vue-element-admin/department/${id}`,
    method: 'delete'
  })
}
