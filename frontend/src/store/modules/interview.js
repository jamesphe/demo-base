import {
  getInterviewList,
  getInterviewDetail,
  createInterview,
  updateInterview,
  deleteInterview,
  checkTimeConflict,
  getInterviewerList,
  submitInterviewEvaluation,
  getInterviewEvaluation,
  getInterviewStatistics,
  sendInterviewNotification,
  getInterviewFeedback,
  submitInterviewFeedback,
  getInterviewPreparation,
  generateInterviewPreparation,
  updateInterviewPreparation,
  getInterviewerFocusPoints,
  saveInterviewerFocusPoints
} from '@/api/interview'

const state = {
  interviewList: [],
  total: 0,
  loading: false,
  currentInterview: null,
  interviewerList: [],
  statistics: null,
  preparation: null,
  focusPoints: null
}

const getters = {
  interviewList: state => state.interviewList,
  total: state => state.total,
  loading: state => state.loading,
  currentInterview: state => state.currentInterview,
  interviewerList: state => state.interviewerList,
  statistics: state => state.statistics,
  preparation: state => state.preparation,
  focusPoints: state => state.focusPoints
}

const mutations = {
  SET_INTERVIEW_LIST: (state, { list, total }) => {
    state.interviewList = list
    state.total = total
  },
  SET_LOADING: (state, loading) => {
    state.loading = loading
  },
  SET_CURRENT_INTERVIEW: (state, interview) => {
    state.currentInterview = interview
  },
  SET_INTERVIEWER_LIST: (state, list) => {
    state.interviewerList = list
  },
  SET_STATISTICS: (state, statistics) => {
    state.statistics = statistics
  },
  SET_PREPARATION: (state, preparation) => {
    state.preparation = preparation
  },
  SET_FOCUS_POINTS: (state, focusPoints) => {
    state.focusPoints = focusPoints
  }
}

const actions = {
  // 获取面试列表
  async getInterviewList({ commit }, params) {
    commit('SET_LOADING', true)
    try {
      const response = await getInterviewList(params)
      if (response.data && response.data.meta) {
        commit('SET_INTERVIEW_LIST', {
          list: response.data.data || [],
          total: response.data.meta.total || 0
        })
      }
      return response.data
    } catch (error) {
      console.error('获取面试列表失败:', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取面试详情
  async getInterviewDetail({ commit }, id) {
    commit('SET_LOADING', true)
    try {
      const response = await getInterviewDetail(id)
      commit('SET_CURRENT_INTERVIEW', response.data)
      return response.data
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 创建面试
  async createInterview({ dispatch }, data) {
    const response = await createInterview(data)
    dispatch('getInterviewList')
    return response.data
  },

  // 更新面试信息
  async updateInterview({ dispatch }, { id, data }) {
    const response = await updateInterview(id, data)
    dispatch('getInterviewList')
    return response.data
  },

  // 删除面试
  async deleteInterview({ dispatch }, id) {
    await deleteInterview(id)
    dispatch('getInterviewList')
  },

  // 检查时间冲突
  async checkTimeConflict(_, data) {
    const response = await checkTimeConflict(data)
    return response.data
  },

  // 获取面试官列表
  async getInterviewerList({ commit }) {
    const response = await getInterviewerList()
    commit('SET_INTERVIEWER_LIST', response.data)
    return response.data
  },

  // 提交面试评估
  async submitInterviewEvaluation({ dispatch }, { id, data }) {
    const response = await submitInterviewEvaluation(id, data)
    dispatch('getInterviewList')
    return response.data
  },

  // 获取面试评估
  async getInterviewEvaluation(_, id) {
    const response = await getInterviewEvaluation(id)
    return response.data
  },

  // 获取面试统计数据
  async getInterviewStatistics({ commit }, params) {
    const response = await getInterviewStatistics(params)
    commit('SET_STATISTICS', response.data)
    return response.data
  },

  // 发送面试通知
  async sendInterviewNotification(_, { id, data }) {
    const response = await sendInterviewNotification(id, data)
    return response.data
  },

  // 获取面试反馈
  async getInterviewFeedback(_, id) {
    const response = await getInterviewFeedback(id)
    return response.data
  },

  // 提交面试反馈
  async submitInterviewFeedback(_, { id, data }) {
    const response = await submitInterviewFeedback(id, data)
    return response.data
  },

  // 获取面试准备材料
  async getInterviewPreparation({ commit }, interviewId) {
    try {
      const response = await getInterviewPreparation(interviewId)
      commit('SET_PREPARATION', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // 生成面试准备材料
  async generateInterviewPreparation({ commit }, { interviewId, data }) {
    try {
      const response = await generateInterviewPreparation(interviewId, data)
      commit('SET_PREPARATION', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // 更新面试准备材料
  async updateInterviewPreparation({ commit }, { interviewId, data }) {
    try {
      const response = await updateInterviewPreparation(interviewId, data)
      commit('SET_PREPARATION', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // 获取面试官关注点
  async getInterviewerFocusPoints({ commit }) {
    try {
      const response = await getInterviewerFocusPoints()
      commit('SET_FOCUS_POINTS', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // 保存面试官关注点
  async saveInterviewerFocusPoints({ commit }, data) {
    try {
      const response = await saveInterviewerFocusPoints(data)
      commit('SET_FOCUS_POINTS', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
} 