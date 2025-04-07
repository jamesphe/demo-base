import request from '@/utils/request'
import { getToken } from '@/utils/auth'

// 上传简历
export function uploadResume(file, positionId, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    const formData = new FormData()
    formData.append('file', file)
    if (positionId) {
      formData.append('job_id', positionId)
    }

    xhr.open('POST', `${process.env.VUE_APP_BASE_API || 'http://localhost:8000'}/resumes/upload`, true)

    // 添加认证头
    const token = getToken()
    if (token) {
      xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    }

    // 设置进度监听
    if (xhr.upload && typeof xhr.upload.addEventListener === 'function') {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const percentCompleted = Math.round((event.loaded * 100) / event.total)
          onProgress({ percent: percentCompleted })
        }
      })
    }

    xhr.onload = function() {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText)
          resolve(response)
        } catch (e) {
          reject(new Error('解析响应失败'))
        }
      } else {
        reject(new Error('上传失败: ' + xhr.status))
      }
    }

    xhr.onerror = function() {
      reject(new Error('网络错误'))
    }

    xhr.send(formData)
  })
}

// 获取简历预览URL
export function getResumePreviewUrl(resumeId) {
  console.log('API: 发起预览URL请求, resumeId:', resumeId)
  return request({
    url: `/resumes/${resumeId}/preview`,
    method: 'get'
  }).then(response => {
    console.log('API: 预览URL请求成功:', response)
    return response
  }).catch(error => {
    console.error('API: 预览URL请求失败:', error)
    throw error
  })
}

// 删除已上传的简历
export function deleteResume(resumeId) {
  return request({
    url: `/resumes/${resumeId}`,
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
