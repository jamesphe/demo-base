import request from '@/utils/request'

// 上传简历
export function uploadResume(data, positionId) {
  // 如果传入了 positionId，将其添加到 FormData 中
  if (positionId) {
    data.append('job_id', positionId)
  }

  return request({
    url: '/resumes/upload',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取简历预览URL
export function getResumePreviewUrl(fileId) {
  return request({
    url: `/resume/${fileId}/preview`,
    method: 'get'
  })
}

// 删除已上传的简历
export function deleteResume(fileId) {
  return request({
    url: `/resume/${fileId}`,
    method: 'delete'
  })
}

// 获取简历解析列表
export function getParseList(params) {
  return request({
    url: '/resumes',
    method: 'get',
    params
  })
}

// 解析简历
export function parseResume(fileUrl) {
  return request({
    url: '/resumes/parse',
    method: 'post',
    data: {
      file_url: fileUrl
    }
  })
}

// 获取解析结果
export function getParseResult(id) {
  return request({
    url: `/resumes/${id}`,
    method: 'get'
  })
}

// 删除解析记录
export function deleteParseRecord(id) {
  return request({
    url: `/resumes/${id}`,
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
    url: `/resumes/${id}`,
    method: 'get',
    params: { id }
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

export function getResumesByAIChat(message) {
  return request({
    url: '/api/resume/ai-chat',
    method: 'post',
    data: { message }
  })
}

export function getChatHistory() {
  return request({
    url: '/api/resume/chat-history',
    method: 'get'
  })
}

export function saveChat(chatData) {
  return request({
    url: '/api/resume/save-chat',
    method: 'post',
    data: chatData
  })
}
