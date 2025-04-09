import request from '@/utils/request'

export function getApplications(params) {
  console.log('Making API request with params:', params)
  console.log('API URL:', '/job-applications')
  return request({
    url: '/job-applications',
    method: 'get',
    params
  })
}

export function updateApplicationStatus(id, data) {
  return request({
    url: `/job-applications/${id}`,
    method: 'put',
    data
  })
}
