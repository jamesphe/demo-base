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

// actions
const actions = {
  // 获取申请列表
  getApplicationList({ commit }, params) {
    commit('SET_LOADING', true)
    return new Promise((resolve, reject) => {
      getApplications(params)
        .then(response => {
          const applications = response.data || []
          commit('SET_APPLICATIONS', applications)
          commit('SET_TOTAL', response.meta?.total || applications.length)
          commit('SET_LOADING', false)
          resolve(applications)
        })
        .catch(error => {
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