import { uploadResume, getResumePreviewUrl, deleteResume } from '@/api/resume'
import { baseURL } from '@/utils/request'
import { getToken } from '@/utils/auth'

const state = {
  uploadedFiles: [],
  currentPreviewUrl: '',
  previewLoading: false
}

const mutations = {
  SET_UPLOADED_FILES: (state, files) => {
    state.uploadedFiles = files
  },
  ADD_UPLOADED_FILE: (state, file) => {
    state.uploadedFiles.push(file)
  },
  REMOVE_UPLOADED_FILE: (state, fileId) => {
    state.uploadedFiles = state.uploadedFiles.filter(file => file.id !== fileId)
  },
  SET_PREVIEW_URL: (state, url) => {
    const token = getToken()
    const separator = url.includes('?') ? '&' : '?'
    state.currentPreviewUrl = url.startsWith('http')
      ? `${url}${separator}token=${token}`
      : `${baseURL}${url}${separator}token=${token}`
  },
  SET_PREVIEW_LOADING: (state, loading) => {
    state.previewLoading = loading
  }
}

const actions = {
  // 上传简历
  async uploadResume({ commit }, { file, positionId, onProgress }) {
    try {
      const response = await uploadResume(file, positionId, onProgress)
      if (response.data) {
        commit('ADD_UPLOADED_FILE', response.data)
      }
      return response.data
    } catch (error) {
      console.error('上传简历失败:', error)
      throw error
    }
  },

  // 获取预览URL
  async getPreviewUrl({ commit }, resumeId) {
    console.log('Store: 开始获取预览URL, resumeId:', resumeId)
    commit('SET_PREVIEW_LOADING', true)
    try {
      const response = await getResumePreviewUrl(resumeId)
      console.log('Store: API响应:', response)
      const url = response?.previewUrl
      console.log('Store: 解析到的URL:', url)
      if (url) {
        commit('SET_PREVIEW_URL', url)
      }
      return url
    } catch (error) {
      console.error('Store: 获取预览URL失败:', error)
      throw error
    } finally {
      commit('SET_PREVIEW_LOADING', false)
    }
  },

  // 删除简历
  async deleteResume({ commit }, fileId) {
    try {
      await deleteResume(fileId)
      commit('REMOVE_UPLOADED_FILE', fileId)
    } catch (error) {
      console.error('删除简历失败:', error)
      throw error
    }
  }
}

const getters = {
  previewUrl: state => state.currentPreviewUrl,
  previewLoading: state => state.previewLoading
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
