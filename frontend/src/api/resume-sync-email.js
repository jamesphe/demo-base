import request from '@/utils/request'

const baseUrl = '/resume-sync-emails'

// 获取邮箱列表
export function fetchList(params) {
  return request({
    url: baseUrl,
    method: 'get',
    params
  })
}

// 获取单个邮箱配置
export function getEmail(id) {
  return request({
    url: `${baseUrl}/${id}`,
    method: 'get'
  })
}

// 创建邮箱配置
export function createEmail(data) {
  return request({
    url: baseUrl,
    method: 'post',
    data
  })
}

// 更新邮箱配置
export function updateEmail(id, data) {
  return request({
    url: `${baseUrl}/${id}`,
    method: 'put',
    data
  })
}

// 删除邮箱配置
export function deleteEmail(id) {
  return request({
    url: `${baseUrl}/${id}`,
    method: 'delete'
  })
}

// 获取邮箱关联的关键词
export function fetchKeywords(emailId) {
  return request({
    url: `${baseUrl}/${emailId}/keywords`,
    method: 'get'
  })
}

// 添加关键词
export function createKeyword(emailId, data) {
  return request({
    url: `${baseUrl}/${emailId}/keywords`,
    method: 'post',
    data
  })
}

// 更新关键词
export function updateKeyword(emailId, keywordId, data) {
  return request({
    url: `${baseUrl}/${emailId}/keywords/${keywordId}`,
    method: 'put',
    data
  })
}

// 删除关键词
export function deleteKeyword(emailId, keywordId) {
  return request({
    url: `${baseUrl}/${emailId}/keywords/${keywordId}`,
    method: 'delete'
  })
}

// 手动触发同步
export function triggerSync(emailId) {
  return request({
    url: `${baseUrl}/${emailId}/sync`,
    method: 'post'
  })
}

// 测试邮箱连接
export function testConnection(data) {
  return request({
    url: `${baseUrl}/test-connection`,
    method: 'post',
    data
  })
} 