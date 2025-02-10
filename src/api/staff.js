import request from '@/utils/request'

// ... 其他代码保持不变

export function deleteStaff(id) {
  return request({
    url: `/vue-element-admin/staff/${id}`,
    method: 'delete'
  })
}
