import { 
  getCandidateList, 
  createCandidate,
  updateCandidate,
  deleteCandidate,
  updateCandidateStatus,
  getCandidateDetail
} from '@/api/candidate'

// 初始状态
const state = {
  candidates: [],
  total: 0,
  loading: false,
  currentCandidate: {}
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
      getCandidateList(params)
        .then(response => {
          // 检查返回数据结构
          console.log('候选人列表API响应:', response)
          // 根据实际API响应结构调整
          if (response.data && Array.isArray(response.data)) {
            // 如果数据直接是数组
            commit('SET_CANDIDATES', response.data)
            // 检查meta是否存在
            if (response.meta && typeof response.meta.total === 'number') {
              commit('SET_TOTAL', response.meta.total)
            } else {
              // 如果没有total信息，则默认为数组长度
              commit('SET_TOTAL', response.data.length)
            }
          } else if (response.data && response.data.items) {
            // 如果数据是标准的items格式
            commit('SET_CANDIDATES', response.data.items)
            commit('SET_TOTAL', response.data.total || 0)
          } else {
            // 兜底处理
            commit('SET_CANDIDATES', [])
            commit('SET_TOTAL', 0)
          }
          resolve(response)
        })
        .catch(error => {
          reject(error)
        })
        .finally(() => {
          commit('SET_LOADING', false)
        })
    })
  },

  // 添加候选人
  addCandidate({ commit }, data) {
    return new Promise((resolve, reject) => {
      createCandidate(data)
        .then(response => {
          resolve(response.data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // createCandidate作为addCandidate的别名
  createCandidate({ dispatch }, data) {
    return dispatch('addCandidate', data)
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
      updateCandidateStatus(id, data)
        .then(response => {
          resolve(response.data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 更新候选人信息
  updateCandidate({ commit }, data) {
    return new Promise((resolve, reject) => {
      updateCandidate(data)
        .then(response => {
          resolve(response.data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 删除候选人
  deleteCandidate({ commit }, id) {
    return new Promise((resolve, reject) => {
      deleteCandidate(id)
        .then(response => {
          resolve(response.data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 获取候选人详情
  getCandidateDetail({ commit }, id) {
    commit('SET_LOADING', true)
    return new Promise((resolve, reject) => {
      getCandidateDetail(id)
        .then(response => {
          commit('SET_CURRENT_CANDIDATE', response.data)
          resolve(response.data)
        })
        .catch(error => {
          reject(error)
        })
        .finally(() => {
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