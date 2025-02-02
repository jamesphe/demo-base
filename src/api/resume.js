import request from '@/utils/request'

// 简历上传
export function uploadResume(data) {
  return request({
    url: '/resume/upload',
    method: 'post',
    data
  })
}

// 获取简历解析列表
export function getParseList(params) {
  return request({
    url: '/resume/parse/list',
    method: 'get',
    params
  })
}

// 解析简历
export function parseResume(id) {
  return request({
    url: `/resume/parse/${id}`,
    method: 'post'
  })
}

// 获取解析结果
export function getParseResult(id) {
  return request({
    url: `/resume/parse/result/${id}`,
    method: 'get'
  })
}

// 删除解析记录
export function deleteParseRecord(id) {
  return request({
    url: `/resume/parse/${id}`,
    method: 'delete'
  })
}

// 获取简历存储列表
export function getStorageList(params) {
  return request({
    url: '/resume/storage/list',
    method: 'get',
    params
  })
}

// 获取存储统计信息
export function getStorageStats() {
  return request({
    url: '/resume/storage/stats',
    method: 'get'
  })
}

// 移动文件存储位置
export function moveStorage(id, location) {
  return request({
    url: `/resume/storage/move/${id}`,
    method: 'put',
    data: { location }
  })
}

// 删除存储文件
export function deleteStorageFile(id) {
  return request({
    url: `/resume/storage/${id}`,
    method: 'delete'
  })
}

// 搜索简历
export function searchResumes(params) {
  return request({
    url: '/resume/search',
    method: 'get',
    params
  })
}

// 获取简历详情
export function getResumeDetail(id) {
  return request({
    url: `/resume/detail/${id}`,
    method: 'get'
  })
}

// 下载简历
export function downloadResume(id) {
  return request({
    url: `/resume/download/${id}`,
    method: 'get',
    responseType: 'blob'
  })
}

// 收藏/取消收藏简历
export function toggleResumeStar(id, starred) {
  return request({
    url: `/resume/star/${id}`,
    method: 'put',
    data: { starred }
  })
}

// 导出搜索结果
export function exportSearchResult(params) {
  return request({
    url: '/resume/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
} 