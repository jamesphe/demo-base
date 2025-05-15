import {
  generateInterviewQuestions,
  generateCandidateAnalysis,
  getQuestionSuggestions,
  getEvaluationSuggestions,
  generateInterviewGuide,
  streamGenerateInterviewGuide
} from '@/api/ai'

const state = {
  questions: null,
  analysis: null,
  suggestions: null,
  evaluationSuggestions: null,
  loading: false,
  error: null
}

const mutations = {
  SET_QUESTIONS: (state, questions) => {
    state.questions = questions
  },
  SET_ANALYSIS: (state, analysis) => {
    state.analysis = analysis
  },
  SET_SUGGESTIONS: (state, suggestions) => {
    state.suggestions = suggestions
  },
  SET_EVALUATION_SUGGESTIONS: (state, suggestions) => {
    state.evaluationSuggestions = suggestions
  },
  SET_LOADING: (state, loading) => {
    state.loading = loading
  },
  SET_ERROR: (state, error) => {
    state.error = error
  }
}

const actions = {
  // 生成面试问题
  async generateQuestions({ commit }, data) {
    try {
      commit('SET_LOADING', true)
      const response = await generateInterviewQuestions(data)
      commit('SET_QUESTIONS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 生成候选人分析
  async generateAnalysis({ commit }, data) {
    try {
      commit('SET_LOADING', true)
      const response = await generateCandidateAnalysis(data)
      commit('SET_ANALYSIS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取问题建议
  async getSuggestions({ commit }, data) {
    try {
      commit('SET_LOADING', true)
      const response = await getQuestionSuggestions(data)
      commit('SET_SUGGESTIONS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取评估建议
  async getEvaluationSuggestions({ commit }, data) {
    try {
      commit('SET_LOADING', true)
      const response = await getEvaluationSuggestions(data)
      commit('SET_EVALUATION_SUGGESTIONS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 生成面试指导文档
  async generateInterviewGuide({ commit }, data) {
    try {
      commit('SET_LOADING', true)
      const response = await generateInterviewGuide(data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 流式生成面试指导文档
  async streamGenerateInterviewGuide({ commit }, { data, onChunk }) {
    try {
      commit('SET_LOADING', true)
      console.log('Vuex动作: 开始流式生成面试指南', data)
      await streamGenerateInterviewGuide(data, onChunk)
    } catch (error) {
      commit('SET_ERROR', error.message)
      console.error('Vuex动作: 流式生成失败', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
} 