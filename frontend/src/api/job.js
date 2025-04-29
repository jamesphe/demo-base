import request from '@/utils/request'

/**
 * 生成职位描述
 * @param {Object} params 请求参数
 * @param {string} params.title 职位名称
 * @param {string} params.job_type 职位类型
 * @param {string} params.department 所属部门
 * @param {string} params.education_required 学历要求
 * @param {string} params.experience_required 工作经验
 * @param {string} params.current_description 当前描述（可选）
 */
export function generateJobDescription(params) {
  return request({
    url: '/jobs/generate-description',
    method: 'post',
    params: {
      title: params.title,
      job_type: params.job_type,
      department: params.department,
      education_required: params.education_required,
      experience_required: params.experience_required,
      current_description: params.current_description
    }
  })
}

/**
 * 生成任职要求
 * @param {Object} params 请求参数
 * @param {string} params.title 职位名称
 * @param {string} params.job_type 职位类型
 * @param {string} params.department 所属部门
 * @param {string} params.education_required 学历要求
 * @param {string} params.experience_required 工作经验
 * @param {string} params.current_requirements 当前要求（可选）
 */
export function generateJobRequirements(params) {
  return request({
    url: '/jobs/generate-requirements',
    method: 'post',
    params: {
      title: params.title,
      job_type: params.job_type,
      department: params.department,
      education_required: params.education_required,
      experience_required: params.experience_required,
      current_requirements: params.current_requirements
    }
  })
} 