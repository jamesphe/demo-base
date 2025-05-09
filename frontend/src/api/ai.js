import request from '@/utils/request'

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