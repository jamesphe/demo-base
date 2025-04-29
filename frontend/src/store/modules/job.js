import { generateJobDescription, generateJobRequirements } from '@/api/job'

const state = {
  jobList: [],
  currentJob: null,
  loading: {
    description: false,
    requirements: false
  },
  // 用于存储取消控制器
  abortControllers: {
    description: null,
    requirements: null
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
  },
  SET_ABORT_CONTROLLER: (state, { type, controller }) => {
    state.abortControllers[type] = controller
  }
}

const actions = {
  // 取消生成
  async cancelGeneration({ commit, state }, { type }) {
    if (state.abortControllers[type]) {
      state.abortControllers[type].abort()
      commit('SET_ABORT_CONTROLLER', { type, controller: null })
      commit('SET_LOADING', { type, value: false })
    }
  },

  // 生成职位描述
  async generateDescription({ commit }, payload) {
    try {
      // 创建取消控制器
      const abortController = new AbortController()
      commit('SET_ABORT_CONTROLLER', { 
        type: 'description', 
        controller: abortController 
      })
      commit('SET_LOADING', { type: 'description', value: true })

      const response = await generateJobDescription({
        ...payload,
        signal: abortController.signal
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
      // 如果是取消请求导致的错误，不显示错误提示
      if (error.name === 'AbortError') {
        return {
          success: false,
          message: '已取消生成'
        }
      }
      console.error('生成职位描述失败:', error)
      return {
        success: false,
        message: 'AI生成失败，请重试'
      }
    } finally {
      commit('SET_ABORT_CONTROLLER', { 
        type: 'description', 
        controller: null 
      })
      commit('SET_LOADING', { type: 'description', value: false })
    }
  },

  // 生成任职要求
  async generateRequirements({ commit }, payload) {
    try {
      // 创建取消控制器
      const abortController = new AbortController()
      commit('SET_ABORT_CONTROLLER', { 
        type: 'requirements', 
        controller: abortController 
      })
      commit('SET_LOADING', { type: 'requirements', value: true })

      const response = await generateJobRequirements({
        ...payload,
        signal: abortController.signal
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
      // 如果是取消请求导致的错误，不显示错误提示
      if (error.name === 'AbortError') {
        return {
          success: false,
          message: '已取消生成'
        }
      }
      console.error('生成任职要求失败:', error)
      return {
        success: false,
        message: 'AI生成失败，请重试'
      }
    } finally {
      commit('SET_ABORT_CONTROLLER', { 
        type: 'requirements', 
        controller: null 
      })
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