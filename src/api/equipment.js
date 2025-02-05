import request from '@/utils/request'

// 获取设备列表
export function getEquipmentList(query) {
  return request({
    url: '/equipment/list',
    method: 'get',
    params: query
  })
}

// 添加设备
export function addEquipment(data) {
  return request({
    url: '/equipment',
    method: 'post',
    data
  })
}

// 更新设备
export function updateEquipment(data) {
  return request({
    url: `/equipment/update/${data.id}`,
    method: 'put',
    params: { id: data.id },
    data
  })
}

// 删除设备
export function deleteEquipment(id) {
  return request({
    url: `/equipment/delete/${id}`,
    method: 'delete',
    params: { id }
  })
}

// 修改获取详情的方法
export function getEquipmentDetail(id) {
  if (!id) {
    return Promise.reject(new Error('ID is required'))
  }
  return request({
    url: `/equipment/detail/${id}`,
    method: 'get',
    params: { id }
  })
}

// 获取实训室选项
export function getRoomOptions() {
  return request({
    url: '/equipment/room-options',
    method: 'get'
  })
}

// 获取负责人选项
export function getManagerOptions() {
  return request({
    url: '/equipment/manager-options',
    method: 'get'
  })
}

// 获取设备申报审核列表
export function getEquipmentApprovalList(query) {
  return request({
    url: '/equipment/approval/list',
    method: 'get',
    params: query
  })
}

// 审核通过设备申请
export function approveEquipment(id) {
  return request({
    url: `/equipment/approval/approve/${id}`,
    method: 'post'
  })
}

// 拒绝设备申请
export function rejectEquipment(data) {
  return request({
    url: `/equipment/approval/reject/${data.id}`,
    method: 'post',
    data
  })
}

// 批量审核通过设备申请
export function batchApproveEquipment(ids) {
  return request({
    url: '/equipment/approval/batch-approve',
    method: 'post',
    data: { ids }
  })
}
