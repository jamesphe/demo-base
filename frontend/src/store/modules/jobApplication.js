import { getApplications, updateApplicationStatus, batchUpdateStatus } from '@/api/job-application'

const state = {
  applications: [],
  total: 0,
  loading: false
}

const mutations = {
  SET_APPLICATIONS: (state, applications) => {
    state.applications = applications
  },
  SET_TOTAL: (state, total) => {
    state.total = total
  },
  SET_LOADING: (state, loading) => {
    state.loading = loading
  }
}

// 数据扁平化处理函数
const flattenApplicationData = (application) => {
  console.log('原始申请数据:', application)
  console.log('职位信息:', application.job)
  
  const { job, ...rest } = application
  const flattenedData = {
    ...rest,
    job_title: job?.title || '',
    department_name: job?.departmentName || '',
    publisher_name: job?.publisherName || '',
    job_id: job?.id,
    // 保留原始job对象，以备其他地方可能需要完整的职位信息
    job: job
  }
  
  console.log('扁平化后的数据:', flattenedData)
  return flattenedData
}

// actions
const actions = {
  // 获取申请列表
  getApplicationList({ commit }, params) {
    console.log('开始获取申请列表, 参数:', params)
    commit('SET_LOADING', true)
    return new Promise((resolve, reject) => {
      getApplications(params)
        .then(response => {
          console.log('API返回原始数据:', response)
          const applications = (response.data || []).map(flattenApplicationData)
          console.log('处理后的申请列表:', applications)
          commit('SET_APPLICATIONS', applications)
          commit('SET_TOTAL', response.meta?.total || applications.length)
          commit('SET_LOADING', false)
          resolve(applications)
        })
        .catch(error => {
          console.error('获取申请列表失败:', error)
          commit('SET_LOADING', false)
          reject(error)
        })
    })
  },

  // 更新申请状态
  updateStatus({ commit }, { id, data }) {
    return new Promise((resolve, reject) => {
      updateApplicationStatus(id, data)
        .then(response => {
          resolve(response.data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },
  
  // 批量更新申请状态
  batchUpdateStatus({ commit }, { ids, data }) {
    return new Promise((resolve, reject) => {
      batchUpdateStatus(ids, data)
        .then(response => {
          resolve(response.data)
        })
        .catch(error => {
          reject(error)
        })
    })
  }
}

const getters = {
  applicationList: state => state.applications,
  total: state => state.total,
  loading: state => state.loading
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 