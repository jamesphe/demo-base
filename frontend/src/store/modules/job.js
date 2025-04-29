import { generateJobDescription, generateJobRequirements } from '@/api/job'

const state = {
  jobList: [],
  currentJob: null,
  loading: {
    description: false,
    requirements: false
  }
}

const mutations = {
  SET_JOB_LIST: (state, jobs) => {
    state.jobList = jobs
  },
  SET_CURRENT_JOB: (state, job) => {
    state.currentJob = job
  },
  SET_LOADING: (state, { type, value }) => {
    state.loading[type] = value
  }
}

const actions = {
  // 生成职位描述
  async generateDescription({ commit }, payload) {
    try {
      commit('SET_LOADING', { type: 'description', value: true })
      const response = await generateJobDescription({
        title: payload.title,
        job_type: payload.job_type,
        department: payload.department,
        education_required: payload.education_required,
        experience_required: payload.experience_required,
        current_description: payload.current_description
      })

      if (response.success) {
        return {
          success: true,
          description: response.description
        }
      } else {
        return {
          success: false,
          message: response.message || 'AI生成失败，请重试'
        }
      }
    } catch (error) {
      console.error('生成职位描述失败:', error)
      return {
        success: false,
        message: 'AI生成失败，请重试'
      }
    } finally {
      commit('SET_LOADING', { type: 'description', value: false })
    }
  },

  // 生成任职要求
  async generateRequirements({ commit }, payload) {
    try {
      commit('SET_LOADING', { type: 'requirements', value: true })
      const response = await generateJobRequirements({
        title: payload.title,
        job_type: payload.job_type,
        department: payload.department,
        education_required: payload.education_required,
        experience_required: payload.experience_required,
        current_requirements: payload.current_requirements
      })

      if (response.success) {
        return {
          success: true,
          requirements: response.requirements
        }
      } else {
        return {
          success: false,
          message: response.message || 'AI生成失败，请重试'
        }
      }
    } catch (error) {
      console.error('生成任职要求失败:', error)
      return {
        success: false,
        message: 'AI生成失败，请重试'
      }
    } finally {
      commit('SET_LOADING', { type: 'requirements', value: false })
    }
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
} 