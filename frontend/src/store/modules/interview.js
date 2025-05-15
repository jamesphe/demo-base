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
  saveInterviewerFocusPoints,
  getInterviewerFeedback,
  submitInterviewerFeedback,
  getInterviewFeedbackSummary,
  generateInterviewPreparationNotes,
  saveInterviewPreparationNotes
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
    console.log('Store: 执行 SET_INTERVIEW_LIST mutation, 数据:', { list, total })
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
      console.log('Store: 开始获取面试列表, 参数:', params)
      const response = await getInterviewList(params)
      console.log('Store: 获取面试列表原始响应:', response)
      
      // 直接使用 response.data，因为 API 已经返回了正确的数据结构
      const list = response.data || []
      const total = response.meta?.total || 0
      
      console.log('Store: 准备提交的数据:', { list, total })
      commit('SET_INTERVIEW_LIST', { list, total })
      
      return list
    } catch (error) {
      console.error('Store: 获取面试列表失败:', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取面试详情
  async getInterviewDetail({ commit }, id) {
    commit('SET_LOADING', true)
    try {
      console.log('Store: 开始获取面试详情, ID:', id)
      const response = await getInterviewDetail(id)
      console.log('Store: 获取到的面试详情:', response)
      
      // 直接使用response，不再访问.data
      commit('SET_CURRENT_INTERVIEW', response)
      return response
    } catch (error) {
      console.error('Store: 获取面试详情失败:', error)
      throw error
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
    // 处理面试官数据，确保正确传递
    const updateData = { ...data };
    if (updateData.interviewers && !updateData.interviewer_ids) {
      updateData.interviewer_ids = updateData.interviewers;
    }
    
    const response = await updateInterview(id, updateData);
    dispatch('getInterviewList');
    return response.data;
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
  },

  // 获取面试反馈
  async getInterviewerFeedback(_, { interviewId, interviewerId }) {
    const response = await getInterviewerFeedback(interviewId, interviewerId)
    console.log('Store: 获取到的面试反馈:', response)
    return response
  },

  // 提交面试反馈
  async submitInterviewerFeedback(_, { id, data }) {
    const response = await submitInterviewerFeedback(id, data)
    return response.data
  },

  // 获取面试反馈摘要
  async getInterviewFeedbackSummary(_, id) {
    try {
      console.log('Store: 开始获取面试反馈汇总, ID:', id)
      const data = await getInterviewFeedbackSummary(id)
      console.log('Store: 获取到的面试反馈汇总数据:', data)
      
      if (data) {
        return data
      } else {
        console.error('Store: 面试反馈汇总数据为空')
        return null
      }
    } catch (error) {
      console.error('Store: 获取面试反馈汇总失败:', error)
      throw error
    }
  },

  // 生成面试准备材料
  async generateInterviewPreparationNotes({ commit }, { interviewId, data }) {
    try {
      const response = await generateInterviewPreparationNotes(interviewId, data)
      commit('SET_PREPARATION', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // 保存面试准备材料
  async saveInterviewPreparationNotes({ commit }, { interviewId, interviewerId, data }) {
    try {
      const response = await saveInterviewPreparationNotes(interviewId, interviewerId, data)
      commit('SET_PREPARATION', response.data)
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