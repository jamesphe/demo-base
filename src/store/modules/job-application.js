import { getApplications, updateApplicationStatus } from '@/api/job-application'
import { getResumeDetail } from '@/api/resume'

const state = {
  applications: [],
  total: 0,
  loading: false,
  matchAnalysis: {
    score: 0,
    details: {
      education: { score: 0, level: 0, comment: '' },
      experience: { score: 0, level: 0, comment: '' },
      skills: { score: 0, level: 0, comment: '', details: [] },
      intention: { score: 0, level: 0, comment: '' },
      salary: { score: 0, level: 0, comment: '' }
    }
  }
}

const mutations = {
  SET_APPLICATIONS: (state, applications) => {
    state.applications = applications
  },
  SET_TOTAL: (state, total) => {
    state.total = total
  },
  SET_LOADING: (state, loading) => {
    state.loading = loading
  },
  SET_MATCH_ANALYSIS: (state, analysis) => {
    state.matchAnalysis = analysis
  }
}

const actions = {
  // 获取职位申请列表
  async getApplicationList({ commit }, params) {
    try {
      commit('SET_LOADING', true)
      const response = await getApplications(params)
      console.log('API Response:', response)
      console.log('Response structure:', {
        hasData: !!response.data,
        dataType: typeof response.data,
        isArray: Array.isArray(response.data),
        dataKeys: response.data ? Object.keys(response.data) : []
      })

      const applications = Array.isArray(response)
        ? response
        : Array.isArray(response.data)
          ? response.data
          : []

      console.log('Processed Applications:', applications)
      commit('SET_APPLICATIONS', applications)
      commit('SET_TOTAL', applications.length)
      return applications
    } catch (error) {
      console.error('获取职位申请列表失败:', error)
      console.error('Error details:', error.response?.data || error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 更新职位申请状态
  async updateStatus({ dispatch }, { id, data }) {
    try {
      await updateApplicationStatus(id, data)
      // 更新成功后重新获取列表
      await dispatch('getApplicationList')
      return true
    } catch (error) {
      console.error('更新职位申请状态失败:', error)
      throw error
    }
  },

  // 修改获取简历详情的 action
  async getResumeDetail(_, resumeId) {
    const response = await getResumeDetail(resumeId)
    // 可以在这里处理数据
    const resumeData = {
      name: response.name,
      gender: response.gender,
      age: response.age,
      phone: response.phone,
      email: response.email,
      experienceYears: response.experienceYears,
      highestEducation: response.highestEducation,
      major: response.major,
      expectedPosition: response.expectedPosition,
      expectedLocation: response.expectedLocation,
      currentPosition: response.currentPosition,
      skills: response.skills || [],
      workHistory: response.workHistory || []
    }
    return resumeData
  }
}

const getters = {
  applicationList: state => state.applications,
  total: state => state.total,
  loading: state => state.loading,
  matchAnalysis: state => state.matchAnalysis,
  matchScore: state => state.matchAnalysis.score,
  matchDetails: state => state.matchAnalysis.details
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
