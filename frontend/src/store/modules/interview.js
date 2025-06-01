import {
  getInterviewList,
  getInterviewDetail,
  createInterview,
  updateInterview,
  deleteInterview,
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
      const response = await getInterviewList(params)
      commit('SET_INTERVIEW_LIST', {
        list: response.data,
        total: response.meta.total
      })
      return response.data
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取面试详情
  async getInterviewDetail({ commit }, id) {
    const response = await getInterviewDetail(id)
    commit('SET_CURRENT_INTERVIEW', response)
    return response
  },

  // 创建面试
  async createInterviews(_, data) {
    const response = await createInterview(data)
    return response.data
  },

  // 更新面试
  async updateInterview(_, { id, data }) {
    const response = await updateInterview(id, data)
    return response.data
  },

  // 删除面试
  async deleteInterview(_, id) {
    const response = await deleteInterview(id)
    return response
  },

  // 获取面试官列表
  async getInterviewerList({ commit }) {
    const response = await getInterviewerList()
    commit('SET_INTERVIEWER_LIST', response.data)
    return response
  },

  // 提交面试评估
  async submitInterviewEvaluation(_, { id, data }) {
    const response = await submitInterviewEvaluation(id, data)
    return response
  },

  // 获取面试评估
  async getInterviewEvaluation(_, id) {
    const response = await getInterviewEvaluation(id)
    return response.data
  },

  // 获取面试统计
  async getInterviewStatistics({ commit }) {
    const response = await getInterviewStatistics()
    commit('SET_STATISTICS', response.data)
    return response.data
  },

  // 发送面试通知
  async sendInterviewNotification(_, { id, data }) {
    const response = await sendInterviewNotification(id, data)
    return response
  },

  // 获取面试反馈
  async getInterviewFeedback(_, id) {
    const response = await getInterviewFeedback(id)
    return response
  },

  // 提交面试反馈
  async submitInterviewFeedback(_, { id, data }) {
    const response = await submitInterviewFeedback(id, data)
    return response
  },

  // 获取面试准备
  async getInterviewPreparation({ commit }, id) {
    try {
      console.log('开始获取面试准备信息，ID:', id)
      const response = await getInterviewPreparation(id)
      console.log('API原始响应:', response)
      console.log('response type:', typeof response)
      
      // 检查响应结构 - API直接返回对象而不是包含data属性的对象
      if (response) {
        console.log('API返回数据字段:', Object.keys(response))
        
        // 直接使用response而不是response.data
        if (response.preparationNotes) {
          console.log('检测到preparationNotes字段，值长度:', response.preparationNotes.length)
          // 添加preparation_notes字段以兼容前端代码
          response.preparation_notes = response.preparationNotes
          console.log('已添加preparation_notes兼容字段')
        }
        
        // 将response直接作为preparation数据
        commit('SET_PREPARATION', response)
        return response
      } else {
        console.error('API响应不包含有效数据')
        return null
      }
    } catch (error) {
      console.error('获取面试准备信息出错:', error)
      throw error
    }
  },

  // 生成面试准备
  async generateInterviewPreparation(_, id) {
    const response = await generateInterviewPreparation(id)
    return response.data
  },

  // 更新面试准备
  async updateInterviewPreparation(_, { id, data }) {
    const response = await updateInterviewPreparation(id, data)
    return response
  },

  // 获取面试官关注点
  async getInterviewerFocusPoints({ commit }, id) {
    const response = await getInterviewerFocusPoints(id)
    commit('SET_FOCUS_POINTS', response.data)
    return response
  },

  // 保存面试官关注点
  async saveInterviewerFocusPoints(_, { id, data }) {
    const response = await saveInterviewerFocusPoints(id, data)
    return response
  },

  // 获取面试官反馈
  async getInterviewerFeedback(_, { interviewId, interviewerId }) {
    const response = await getInterviewerFeedback(interviewId, interviewerId)
    return response
  },

  // 提交面试官反馈
  async submitInterviewerFeedback(_, { id, data }) {
    const response = await submitInterviewerFeedback(id, data)
    return response
  },

  // 获取面试反馈总结
  async getInterviewFeedbackSummary(_, id) {
    const response = await getInterviewFeedbackSummary(id)
    return response
  },

  // 生成面试准备笔记
  async generateInterviewPreparationNotes(_, id) {
    const response = await generateInterviewPreparationNotes(id)
    return response
  },

  // 保存面试准备笔记
  async saveInterviewPreparationNotes(_, { id, data }) {
    const response = await saveInterviewPreparationNotes(id, data)
    return response
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
} 