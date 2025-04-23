import request from '@/utils/request'

// 初始状态
const state = {
  candidates: [],
  total: 0,
  loading: false,
  currentCandidate: null
}

// getters
const getters = {
  candidates: state => state.candidates,
  total: state => state.total,
  loading: state => state.loading,
  currentCandidate: state => state.currentCandidate
}

// actions
const actions = {
  // 获取候选人列表
  getCandidateList({ commit }, params) {
    commit('SET_LOADING', true)
    return new Promise((resolve, reject) => {
      request({
        url: '/api/candidates',
        method: 'get',
        params
      }).then(response => {
        commit('SET_CANDIDATES', response.data.data)
        commit('SET_TOTAL', response.data.total)
        resolve(response.data)
      }).catch(error => {
        reject(error)
      }).finally(() => {
        commit('SET_LOADING', false)
      })
    })
  },

  // 添加候选人
  addCandidate({ commit }, data) {
    return new Promise((resolve, reject) => {
      request({
        url: '/api/candidates',
        method: 'post',
        data
      }).then(response => {
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 从职位申请添加候选人
  addCandidatesFromApplications({ commit }, data) {
    return new Promise((resolve, reject) => {
      console.log('正在发送候选人数据:', data);
      request({
        url: '/job-applications/add-candidates',
        method: 'post',
        data
      }).then(response => {
        console.log('添加候选人API原始响应:', response);
        console.log('响应数据类型:', typeof response);
        console.log('响应数据结构:', response ? Object.keys(response) : 'null');
        
        // 直接返回response，因为在request拦截器中已经提取了data
        resolve(response);
      }).catch(error => {
        console.error('添加候选人API错误:', error);
        reject(error);
      });
    });
  },

  // 更新候选人状态
  updateCandidateStatus({ commit }, { id, data }) {
    return new Promise((resolve, reject) => {
      request({
        url: `/api/candidates/${id}/status`,
        method: 'put',
        data
      }).then(response => {
        resolve(response.data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 获取候选人详情
  getCandidateDetail({ commit }, id) {
    commit('SET_LOADING', true)
    return new Promise((resolve, reject) => {
      request({
        url: `/api/candidates/${id}`,
        method: 'get'
      }).then(response => {
        commit('SET_CURRENT_CANDIDATE', response.data)
        resolve(response.data)
      }).catch(error => {
        reject(error)
      }).finally(() => {
        commit('SET_LOADING', false)
      })
    })
  }
}

// mutations
const mutations = {
  SET_CANDIDATES: (state, candidates) => {
    state.candidates = candidates
  },
  SET_TOTAL: (state, total) => {
    state.total = total
  },
  SET_LOADING: (state, loading) => {
    state.loading = loading
  },
  SET_CURRENT_CANDIDATE: (state, candidate) => {
    state.currentCandidate = candidate
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
} 