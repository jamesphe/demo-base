import { uploadResume, getResumePreviewUrl, deleteResume } from '@/api/resume'

const state = {
  uploadedFiles: [],
  currentPreviewUrl: ''
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
    state.currentPreviewUrl = url
  }
}

const actions = {
  // 上传简历
  async uploadResume({ commit }, { file, positionId, onProgress }) {
    try {
      const response = await uploadResume(file, positionId)
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
  async getPreviewUrl({ commit }, fileId) {
    try {
      const response = await getResumePreviewUrl(fileId)
      const url = response.data?.url
      if (url) {
        commit('SET_PREVIEW_URL', url)
      }
      return url
    } catch (error) {
      console.error('获取预览URL失败:', error)
      throw error
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

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
