import request from '@/utils/request'

// 获取申请列表
export function getApplications(params) {
  return request({
    url: '/job-applications',
    method: 'get',
    params
  })
}

// 更新申请状态
export function updateApplicationStatus(id, data) {
  return request({
    url: `/job-applications/${id}`,
    method: 'put',
    data
  })
}

// 批量更新申请状态
export function batchUpdateStatus(ids, data) {
  // 确保ids是数组
  const requestData = {
    ids: Array.isArray(ids) ? ids : [ids],
    ...data
  };
  
  return request({
    url: '/job-applications/batch-status',
    method: 'put',
    data: requestData
  });
}

// 将申请者添加为候选人并更新申请状态（一步完成）
export function convertApplicationsToCandidates(applicationData) {
  return request({
    url: '/job-applications/convert-to-candidates',
    method: 'post',
    data: applicationData
  });
}
