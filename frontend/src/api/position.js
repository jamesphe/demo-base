import request from '@/utils/request'

/**
 * 获取职位列表
 * @param {Object} params 查询参数
 * @param {Number} params.page 当前页码
 * @param {Number} params.limit 每页条数
 * @param {String} params.status 职位状态 (active, closed, draft)
 * @param {String} params.keyword 搜索关键词
 * @param {String} params.department 部门ID
 * @returns {Promise} 返回职位列表
 */
export function getPositionList(params) {
  return request({
    url: '/jobs',
    method: 'get',
    params
  })
}

/**
 * 获取职位详情
 * @param {Number} id 职位ID
 * @returns {Promise} 返回职位详情
 */
export function getPositionDetail(id) {
  return request({
    url: `/jobs/${id}`,
    method: 'get'
  })
}

/**
 * 创建职位
 * @param {Object} data 职位数据
 * @returns {Promise} 返回创建结果
 */
export function createPosition(data) {
  return request({
    url: '/jobs',
    method: 'post',
    data
  })
}

/**
 * 更新职位
 * @param {Number} id 职位ID
 * @param {Object} data 职位数据
 * @returns {Promise} 返回更新结果
 */
export function updatePosition(id, data) {
  return request({
    url: `/jobs/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除职位
 * @param {Number} id 职位ID
 * @returns {Promise} 返回删除结果
 */
export function deletePosition(id) {
  return request({
    url: `/jobs/${id}`,
    method: 'delete'
  })
}

/**
 * 修改职位状态
 * @param {Number} id 职位ID
 * @param {String} status 状态(active, closed, draft)
 * @returns {Promise} 返回操作结果
 */
export function updatePositionStatus(id, status) {
  return request({
    url: `/jobs/${id}/status`,
    method: 'patch',
    data: { status }
  })
}
