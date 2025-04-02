import { getPendingTrials, getTrialList, approveTrial, rejectTrial } from '@/api/trial'

const state = {
  list: [],
  total: 0,
  listLoading: false,
  meta: {
    page: 1,
    per_page: 10,
    total_pages: 1
  }
}

const mutations = {
  SET_LIST: (state, list) => {
    state.list = list
  },
  SET_META: (state, meta) => {
    state.meta = meta
    state.total = meta.total
  },
  SET_LOADING: (state, loading) => {
    state.listLoading = loading
  }
}

const actions = {
  // 获取待审核列表
  getPendingList({ commit }, params) {
    commit('SET_LOADING', true)
    return new Promise((resolve, reject) => {
      getPendingTrials(params)
        .then(response => {
          const { data, meta } = response
          commit('SET_LIST', data)
          commit('SET_META', meta)
          commit('SET_LOADING', false)
          resolve(response)
        })
        .catch(error => {
          commit('SET_LOADING', false)
          reject(error)
        })
    })
  },

  // 获取所有试用列表
  getList({ commit }, params) {
    commit('SET_LOADING', true)
    return new Promise((resolve, reject) => {
      getTrialList(params)
        .then(response => {
          const { data, meta } = response
          commit('SET_LIST', data)
          commit('SET_META', meta)
          commit('SET_LOADING', false)
          resolve(response)
        })
        .catch(error => {
          commit('SET_LOADING', false)
          reject(error)
        })
    })
  },

  // 审批通过
  approveTrial({ commit }, { id, data }) {
    return new Promise((resolve, reject) => {
      approveTrial(id, data)
        .then(response => {
          resolve(response)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  // 拒绝申请
  rejectTrial({ dispatch }, { id, reason }) {
    return new Promise((resolve, reject) => {
      rejectTrial(id, { reason })
        .then(response => {
          dispatch('getList')
          resolve(response)
        })
        .catch(error => {
          reject(error)
        })
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
