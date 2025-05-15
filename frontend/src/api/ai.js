import request from '@/utils/request'
import { getToken, formatToken } from '@/utils/auth'
import { baseURL } from '@/utils/request'

// 生成面试问题
export function generateInterviewQuestions(data) {
  return request({
    url: '/ai/interview/questions',
    method: 'post',
    data
  })
}

// 生成候选人背景分析
export function generateCandidateAnalysis(data) {
  return request({
    url: '/ai/interview/analysis',
    method: 'post',
    data
  })
}

// 获取面试问题建议
export function getQuestionSuggestions(data) {
  return request({
    url: '/ai/interview/suggestions',
    method: 'post',
    data
  })
}

// 获取面试评估建议
export function getEvaluationSuggestions(data) {
  return request({
    url: '/ai/interview/evaluation-suggestions',
    method: 'post',
    data
  })
}

// 生成面试指导文档
export function generateInterviewGuide(data) {
  return request({
    url: '/ai/interview/guide',
    method: 'post',
    data
  })
}

// 流式生成面试指导文档
export async function streamGenerateInterviewGuide(data, onChunk) {
  try {
    // 使用与request一致的baseURL
    const url = `${baseURL}/ai/interview/guide/stream`
    
    // 获取token，保持与request一致的授权方式
    const token = getToken()
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream'
    }
    
    if (token) {
      headers['Authorization'] = formatToken(token)
    }
    
    const controller = new AbortController()
    // 设置30秒超时
    const timeoutId = setTimeout(() => controller.abort(), 30000)
    
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
      credentials: 'include', // 与request保持一致的凭证设置
      signal: controller.signal,
      keepalive: true // 尝试保持连接活跃
    })
    
    // 清除超时计时器
    clearTimeout(timeoutId)

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText || '未知错误'}`)
    }

    const contentType = response.headers.get('content-type')
    
    // 验证内容类型
    if (!contentType || !contentType.includes('text/event-stream')) {
      console.warn('响应内容类型不是预期的text/event-stream:', contentType)
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        // 处理缓冲区中可能剩余的数据
        if (buffer.trim()) {
          onChunk(buffer)
        }
        break
      }

      // 解码接收到的数据
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk
      
      if (buffer.trim()) {
        onChunk(buffer)
        buffer = '' // 清空缓冲区
      }
    }
  } catch (error) {
    // 检查是否是超时错误
    if (error.name === 'AbortError') {
      throw new Error('请求超时，请稍后重试')
    }
    
    // 检查是否是网络错误
    if (error.message.includes('network')) {
      throw new Error('网络连接错误，请检查网络连接并重试')
    }
    
    throw error
  }
} 