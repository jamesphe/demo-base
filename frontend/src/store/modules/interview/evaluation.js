import {
  submitInterviewEvaluation,
  getInterviewEvaluation,
  updateInterviewEvaluation,
  getNextStepOptions,
  proceedToNextStep
} from '@/api/interview'

const state = {
  interviewEvaluation: null,
  nextStepOptions: [],
  loadingEvaluation: false,
  submittingEvaluation: false,
  loadingNextSteps: false,
  executingNextStep: false
}

const mutations = {
  SET_INTERVIEW_EVALUATION(state, evaluation) {
    state.interviewEvaluation = evaluation
  },
  SET_NEXT_STEP_OPTIONS(state, options) {
    state.nextStepOptions = options
  },
  SET_LOADING_EVALUATION(state, loading) {
    state.loadingEvaluation = loading
  },
  SET_SUBMITTING_EVALUATION(state, submitting) {
    state.submittingEvaluation = submitting
  },
  SET_LOADING_NEXT_STEPS(state, loading) {
    state.loadingNextSteps = loading
  },
  SET_EXECUTING_NEXT_STEP(state, executing) {
    state.executingNextStep = executing
  }
}

const actions = {
  // 获取面试评估
  async getEvaluation({ commit }, interviewId) {
    commit('SET_LOADING_EVALUATION', true)
    try {
      const response = await getInterviewEvaluation(interviewId)
      commit('SET_INTERVIEW_EVALUATION', response.data)
      return response.data
    } catch (error) {
      console.error('获取面试评估失败:', error)
      return null
    } finally {
      commit('SET_LOADING_EVALUATION', false)
    }
  },

  // 提交面试评估
  async submitEvaluation({ commit }, { interviewId, evaluationData }) {
    commit('SET_SUBMITTING_EVALUATION', true)
    try {
      const response = await submitInterviewEvaluation(interviewId, evaluationData)
      commit('SET_INTERVIEW_EVALUATION', response.data)
      return response.data
    } catch (error) {
      console.error('提交面试评估失败:', error)
      throw error
    } finally {
      commit('SET_SUBMITTING_EVALUATION', false)
    }
  },

  // 更新面试评估
  async updateEvaluation({ commit }, { interviewId, evaluationData }) {
    commit('SET_SUBMITTING_EVALUATION', true)
    try {
      const response = await updateInterviewEvaluation(interviewId, evaluationData)
      commit('SET_INTERVIEW_EVALUATION', response.data)
      return response.data
    } catch (error) {
      console.error('更新面试评估失败:', error)
      throw error
    } finally {
      commit('SET_SUBMITTING_EVALUATION', false)
    }
  },

  // 获取下一步选项
  async getNextSteps({ commit }, interviewId) {
    commit('SET_LOADING_NEXT_STEPS', true)
    try {
      const response = await getNextStepOptions(interviewId)
      commit('SET_NEXT_STEP_OPTIONS', response.data)
      return response.data
    } catch (error) {
      console.error('获取下一步选项失败:', error)
      commit('SET_NEXT_STEP_OPTIONS', [])
      return []
    } finally {
      commit('SET_LOADING_NEXT_STEPS', false)
    }
  },

  // 执行下一步操作
  async executeNextStep({ commit }, { interviewId, nextStep }) {
    commit('SET_EXECUTING_NEXT_STEP', true)
    try {
      const response = await proceedToNextStep(interviewId, nextStep)
      return response.data
    } catch (error) {
      console.error('执行下一步操作失败:', error)
      throw error
    } finally {
      commit('SET_EXECUTING_NEXT_STEP', false)
    }
  }
}

const getters = {
  evaluation: state => state.interviewEvaluation,
  nextSteps: state => state.nextStepOptions,
  isLoadingEvaluation: state => state.loadingEvaluation,
  isSubmittingEvaluation: state => state.submittingEvaluation,
  isLoadingNextSteps: state => state.loadingNextSteps,
  isExecutingNextStep: state => state.executingNextStep
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 