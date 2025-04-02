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
  // 获取租户列表
  async getList({ commit }, params) {
    try {
      commit('SET_LOADING', true)
      const response = await getTenantList(params)
      commit('SET_LIST', response.data)
      commit('SET_TOTAL', response.meta.total)
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 创建租户
  async createTenant({ dispatch }, data) {
    await createTenant(data)
    return dispatch('getList', { page: 1, limit: 20 })
  },

  // 更新租户
  async updateTenant({ dispatch }, { id, data }) {
    await updateTenant(id, data)
    return dispatch('getList', { page: 1, limit: 20 })
  },

  // 删除租户
  async deleteTenant({ dispatch }, id) {
    await deleteTenant(id)
    return dispatch('getList', { page: 1, limit: 20 })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
