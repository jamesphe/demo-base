import {
  getPositionList,
  createPosition,
  updatePosition,
  deletePosition,
  publishPosition,
  getPositionDetail
} from '@/api/position'

const state = {
  list: [],
  total: 0,
  loading: false,
  currentPosition: null
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
  },
  SET_CURRENT_POSITION: (state, position) => {
    state.currentPosition = position
  }
}

const actions = {
  // 获取职位列表
  async getList({ commit }, params) {
    try {
      commit('SET_LOADING', true)
      const response = await getPositionList(params)
      console.log(response)
      commit('SET_LIST', response.data)
      commit('SET_TOTAL', response.meta.total)
      return response
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 创建职位
  async createPosition({ dispatch }, data) {
    const response = await createPosition(data)
    await dispatch('getList')
    return response
  },

  // 更新职位
  async updatePosition({ dispatch }, { id, data }) {
    const response = await updatePosition(id, data)
    await dispatch('getList')
    return response
  },

  // 删除职位
  async deletePosition({ dispatch }, id) {
    const response = await deletePosition(id)
    await dispatch('getList')
    return response
  },

  // 发布职位
  async publishPosition({ dispatch }, data) {
    const response = await publishPosition(data)
    return response
  },

  // 获取职位详情
  async getPositionDetail({ commit }, id) {
    const response = await getPositionDetail(id)
    commit('SET_CURRENT_POSITION', response)
    return response
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
