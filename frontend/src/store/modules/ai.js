import {
  generateInterviewQuestions,
  generateCandidateAnalysis,
  getQuestionSuggestions,
  getEvaluationSuggestions
} from '@/api/ai'

const state = {
  questions: null,
  analysis: null,
  suggestions: null,
  evaluationSuggestions: null,
  loading: false
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
  }
}

const actions = {
  // 生成面试问题
  async generateQuestions({ commit }, data) {
    commit('SET_LOADING', true)
    try {
      const response = await generateInterviewQuestions(data)
      commit('SET_QUESTIONS', response.data)
      return response.data
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 生成候选人背景分析
  async generateAnalysis({ commit }, data) {
    commit('SET_LOADING', true)
    try {
      const response = await generateCandidateAnalysis(data)
      commit('SET_ANALYSIS', response.data)
      return response.data
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取面试问题建议
  async getSuggestions({ commit }, data) {
    commit('SET_LOADING', true)
    try {
      const response = await getQuestionSuggestions(data)
      commit('SET_SUGGESTIONS', response.data)
      return response.data
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取面试评估建议
  async getEvaluationSuggestions({ commit }, data) {
    commit('SET_LOADING', true)
    try {
      const response = await getEvaluationSuggestions(data)
      commit('SET_EVALUATION_SUGGESTIONS', response.data)
      return response.data
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