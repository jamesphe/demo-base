import request from '@/utils/request'

// 创建面试
export function createInterview(data) {
  // 确保面试官列表被正确传递
  const postData = { ...data }
  if (postData.interviewers && !postData.interviewer_ids) {
    postData.interviewer_ids = postData.interviewers
  }
  
  return request({
    url: '/interviews',
    method: 'post',
    data: postData
  })
}

// 获取面试列表
export function getInterviewList(params) {
  return request({
    url: '/interviews',
    method: 'get',
    params
  })
}

// 获取面试详情
export function getInterviewDetail(id) {
  return request({
    url: `/interviews/${id}`,
    method: 'get'
  })
}

// 更新面试信息
export function updateInterview(id, data) {
  // 确保面试官列表被正确传递
  const postData = { ...data }
  if (postData.interviewers && !postData.interviewer_ids) {
    postData.interviewer_ids = postData.interviewers
  }
  
  return request({
    url: `/interviews/${id}`,
    method: 'put',
    data: postData
  })
}

// 删除面试
export function deleteInterview(id) {
  return request({
    url: `/interviews/${id}`,
    method: 'delete'
  })
}

// 检查面试时间冲突
export function checkTimeConflict(data) {
  return request({
    url: '/interviews/check-time-conflict',
    method: 'post',
    data
  })
}

// 获取面试官列表
export function getInterviewerList() {
  return request({
    url: '/interviews/interviewers',
    method: 'get'
  })
}

// 提交面试评估
export function submitInterviewEvaluation(id, data) {
  return request({
    url: `/interviews/${id}/evaluation`,
    method: 'post',
    data
  })
}

// 获取面试评估详情
export function getInterviewEvaluation(id) {
  return request({
    url: `/interviews/${id}/evaluation`,
    method: 'get'
  })
}

// 获取面试准备材料
export function getInterviewPreparation(interviewId) {
  return request({
    url: `/interviews/${interviewId}/preparation`,
    method: 'get'
  })
}

// 生成面试准备材料
export function generateInterviewPreparation(interviewId, data) {
  return request({
    url: `/interviews/${interviewId}/preparation/generate`,
    method: 'post',
    data
  })
}

// 更新面试准备材料
export function updateInterviewPreparation(interviewId, data) {
  return request({
    url: `/interviews/${interviewId}/preparation`,
    method: 'put',
    data
  })
}

// 获取面试官关注点
export function getInterviewerFocusPoints() {
  return request({
    url: '/interviews/interviewers/focus-points',
    method: 'get'
  })
}

// 保存面试官关注点
export function saveInterviewerFocusPoints(data) {
  return request({
    url: '/interviewers/focus-points',
    method: 'post',
    data
  })
}

// 获取面试统计数据
export function getInterviewStatistics(params) {
  return request({
    url: '/interviews/statistics',
    method: 'get',
    params
  })
}

// 发送面试通知
export function sendInterviewNotification(id, data) {
  return request({
    url: `/interviews/${id}/notification`,
    method: 'post',
    data
  })
}

// 获取面试反馈
export function getInterviewFeedback(id) {
  return request({
    url: `/interviews/${id}/feedback`,
    method: 'get'
  })
}

// 提交面试反馈
export function submitInterviewFeedback(id, data) {
  return request({
    url: `/interviews/${id}/feedback`,
    method: 'post',
    data
  })
}

// 获取面试官反馈
export function getInterviewerFeedback(interviewId, interviewerId) {
  return request({
    url: `/interviews/${interviewId}/feedback/${interviewerId}`,
    method: 'get'
  })
}

// 提交面试官反馈
export function submitInterviewerFeedback(interviewId, data) {
  return request({
    url: `/interviews/${interviewId}/feedback`,
    method: 'put',
    data
  })
}

// 获取面试反馈汇总
export function getInterviewFeedbackSummary(interviewId) {
  return request({
    url: `/interviews/${interviewId}/feedback-summary`,
    method: 'get'
  }).then(response => {
    // 直接用 response（因为 request.js 返回的就是对象）
    const raw = response.data || response;
    if (!raw || !raw.interviewId) {
      console.error('API返回数据结构异常:', raw);
      return null;
    }
    // 字段转换
    const convertedData = {
      interview_id: raw.interviewId,
      average_score: raw.averageScore,
      interviewer_count: raw.interviewerCount,
      completed_count: raw.completedCount,
      recommendation_summary: raw.recommendationSummary || {},
      feedbacks: (raw.feedbacks || []).map(feedback => ({
        feedback: feedback.feedback,
        evaluation_score: feedback.evaluationScore,
        technical_evaluation: feedback.technicalEvaluation,
        comprehensive_evaluation: feedback.comprehensiveEvaluation,
        strengths: feedback.strengths,
        weaknesses: feedback.weaknesses,
        hiring_recommendation: feedback.hiringRecommendation,
        preparation_notes: feedback.preparationNotes,
        process_record: feedback.processRecord,
        interview_id: feedback.interviewId,
        interviewer_id: feedback.interviewerId,
        status: feedback.status,
        created_at: feedback.createdAt,
        updated_at: feedback.updatedAt,
        interviewer_name: feedback.interviewerName,
        interviewer_title: feedback.interviewerTitle
      })),
      key_strengths: raw.keyStrengths || [],
      key_weaknesses: raw.keyWeaknesses || [],
      technical_averages: {
        coding_ability: raw.technicalAverages?.codingAbility,
        problem_solving: raw.technicalAverages?.problemSolving,
        system_design: raw.technicalAverages?.systemDesign,
        algorithm: raw.technicalAverages?.algorithm,
        knowledge_depth: raw.technicalAverages?.knowledgeDepth,
        knowledge_breadth: raw.technicalAverages?.knowledgeBreadth
      },
      comprehensive_averages: {
        communication: raw.comprehensiveAverages?.communication,
        teamwork: raw.comprehensiveAverages?.teamwork,
        learning_ability: raw.comprehensiveAverages?.learningAbility,
        pressure_handling: raw.comprehensiveAverages?.pressureHandling,
        cultural_fit: raw.comprehensiveAverages?.culturalFit
      }
    };
    return convertedData;
  }).catch(error => {
    console.error('API响应失败:', error)
    throw error
  })
}

// AI生成面试准备材料
export function generateInterviewPreparationNotes(interviewId, interviewerId, data) {
  return request({
    url: `/interviews/${interviewId}/interviewers/${interviewerId}/preparation-notes/generate`,
    method: 'post',
    data
  })
}

// 保存面试准备材料
export function saveInterviewPreparationNotes(interviewId, interviewerId, data) {
  return request({
    url: `/interviews/${interviewId}/interviewers/${interviewerId}/preparation-notes`,
    method: 'put',
    data: { preparation_notes: data }
  })
} 