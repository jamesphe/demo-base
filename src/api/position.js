import request from '@/utils/request'

// 查询岗位列表
export function listPosition(query) {
  console.log('API listPosition called with query:', query)
  return request({
    url: '/vue-element-admin/position/list',
    method: 'get',
    params: {
      pageNum: Number(query.pageNum || 1),
      pageSize: Number(query.pageSize || 10),
      name: query.name,
      code: query.code,
      type: query.type ? Number(query.type) : undefined,
      status: query.status ? Number(query.status) : undefined
    }
  }).then(response => {
    console.log('API response:', response)
    return response
  }).catch(error => {
    console.error('API error:', error)
    throw error
  })
}

// 查询岗位详细
export function getPosition(id) {
  console.log('API getPosition called with id:', id)
  return request({
    url: `/vue-element-admin/position/${id}`,
    method: 'get'
  })
}

// 新增岗位
export function addPosition(data) {
  console.log('API addPosition called with data:', data)
  return request({
    url: '/vue-element-admin/position',
    method: 'post',
    data
  })
}

// 修改岗位
export function updatePosition(data) {
  console.log('API updatePosition called with data:', data)
  return request({
    url: '/vue-element-admin/position',
    method: 'put',
    data
  })
}

// 删除岗位
export function deletePosition(id) {
  return request({
    url: `/vue-element-admin/position/${id}`,
    method: 'delete'
  })
}
