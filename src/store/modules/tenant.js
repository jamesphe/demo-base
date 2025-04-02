import { getTenantList, createTenant, updateTenant, deleteTenant } from '@/api/tenant'

const state = {
  list: [],
  total: 0,
  loading: false
}

const mutations = {
  SET_LIST: (state, list) => {
    state.list = list
  },
  SET_TOTAL: (state, total) => {
    state.total = total
  },
  SET_LOADING: (state, loading) => {
    state.loading = loading
  }
}

const actions = {
  getList({ commit }, params) {
    commit('SET_LOADING', true)
    return new Promise((resolve, reject) => {
      getTenantList(params)
        .then(response => {
          commit('SET_LIST', response.data)
          commit('SET_TOTAL', response.data.length)
          commit('SET_LOADING', false)
          resolve(response)
        })
        .catch(error => {
          commit('SET_LOADING', false)
          reject(error)
        })
    })
  },

  createTenant({ dispatch }, data) {
    return new Promise((resolve, reject) => {
      createTenant(data)
        .then(response => {
          dispatch('getList')
          resolve(response)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  updateTenant({ dispatch }, { id, data }) {
    return new Promise((resolve, reject) => {
      updateTenant(id, data)
        .then(response => {
          dispatch('getList')
          resolve(response)
        })
        .catch(error => {
          reject(error)
        })
    })
  },

  deleteTenant({ dispatch }, id) {
    return new Promise((resolve, reject) => {
      deleteTenant(id)
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
