import { uploadResume, getResumePreviewUrl, deleteResume, parseResume } from '@/api/resume'
import { baseURL } from '@/utils/request'
import { getToken } from '@/utils/auth'
import { searchResumes, downloadResume, toggleResumeStar, exportSearchResult, getResumeDetail } from '@/api/resume'

const educationMap = {
  'college': '大专',
  'bachelor': '本科',
  'master': '硕士',
  'doctor': '博士',
  'highschool': '高中',
  'other': '其他'
}

// 添加统一的格式化函数
const formatResumeData = (data) => {
  if (!data) return null

  return {
    id: data.id,
    name: data.name,
    age: data.age,
    gender: data.gender,
    education: data.highestEducation || educationMap[data.education] || data.education,
    experience: data.experienceYears,
    phone: data.phone,
    email: data.email,
    currentPosition: data.currentPosition,
    expectedPosition: data.expectedPosition,
    expectedSalary: data.expectedSalary,
    skills: Array.isArray(data.skills) ? data.skills.map(skill => ({
      name: typeof skill === 'string' ? skill : skill.name,
      level: typeof skill === 'string' ? null : skill.level
    })) : [],
    workExperience: (data.workHistory || data.workExperience || []).map(work => ({
      company: work.company,
      position: work.position,
      startDate: work.startDate || work.start_date,
      endDate: work.endDate || work.end_date,
      description: work.description,
      achievements: work.achievements || []
    })),
    educationDetail: (data.eduExperience || data.educationDetail || []).map(edu => ({
      school: edu.school,
      major: edu.major,
      degree: edu.degree,
      startDate: edu.startDate || edu.start_date,
      endDate: edu.endDate || edu.end_date,
      achievements: edu.achievements || []
    })),
    projectExperience: (data.projectExperience || []).map(project => ({
      name: project.name,
      role: project.role,
      company: project.company,
      startDate: project.startDate,
      endDate: project.endDate,
      description: project.description,
      responsibilities: typeof project.responsibilities === 'string'
        ? [project.responsibilities]
        : Array.isArray(project.responsibilities)
          ? project.responsibilities
          : [],
      achievements: Array.isArray(project.achievements) ? project.achievements : [],
      technologies:
        typeof project.technologies === 'string'
          ? project.technologies
          : Array.isArray(project.technologies)
            ? project.technologies
            : project.technologies
              ? String(project.technologies)
              : ''
    })),
    status: data.reviewStatus || data.status || 'pending',
    currentCompany: data.currentCompany,
    currentCity: data.city || data.currentCity || data.currentAddress,
    expectedLocation: data.expectedLocation,
    currentSalary: data.currentSalary,
    starred: data.starred || false,
    updateTime: data.updatedAt || data.updateTime,
    fileName: data.fileName
  }
}

const state = {
  uploadedFiles: [],
  currentPreviewUrl: '',
  previewLoading: false,
  searchResult: {
    items: [],
    total: 0
  },
  loading: false,
  error: null,
  detailLoading: false,
  currentDetail: null
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
    console.log(`开始设置预览URL: ${url}`);
    const token = getToken()
    console.log(`获取到的token: ${token}`);
    const separator = url.includes('?') ? '&' : '?'
    
    // 如果URL已经包含完整的域名，直接使用
    if (url.startsWith('http')) {
      console.log('URL已包含完整的域名，直接使用');
      state.currentPreviewUrl = `${url}${separator}token=${token}`
      return
    }
    
    // 如果URL已经包含/api/v1前缀，移除前缀后使用
    if (url.startsWith('/api/v1')) {
      console.log('URL已包含/api/v1前缀，移除前缀后使用');
      state.currentPreviewUrl = `${url.substring(7)}${separator}token=${token}`
      return
    }
    
    // 否则添加baseURL
    console.log('URL不包含域名或/api/v1前缀，添加baseURL');
    state.currentPreviewUrl = `${url}${separator}token=${token}`
    console.log(`最终设置的预览URL: ${state.currentPreviewUrl}`);
  },
  SET_PREVIEW_LOADING: (state, loading) => {
    state.previewLoading = loading
  },
  SET_SEARCH_RESULT(state, { items, total }) {
    state.searchResult = {
      items: items || [],
      total: total || 0
    }
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  UPDATE_RESUME_STAR(state, { id, starred }) {
    const item = state.searchResult.items.find(item => item.id === id)
    if (item) {
      item.starred = starred
    }
  },
  SET_DETAIL_LOADING(state, loading) {
    state.detailLoading = loading
  },
  SET_CURRENT_DETAIL(state, detail) {
    state.currentDetail = detail
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
  },

  // 重试简历处理
  async retryResumeProcessing({ commit }, resumeId) {
    try {
      const response = await parseResume(resumeId)
      if (response.data) {
        // 更新文件处理状态
        const file = state.uploadedFiles.find(f => f.id === resumeId)
        if (file) {
          file.processingStatus = 'processing'
        }
      }
      return response.data
    } catch (error) {
      console.error('重试简历处理失败:', error)
      throw error
    }
  },

  async searchResumes({ commit }, params) {
    console.log('开始搜索简历，参数:', params)
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    try {
      console.log('发送API请求到 /resumes/search')
      if (params.education) {
        params.education = educationMap[params.education] || params.education
      }
      const response = await searchResumes(params)
      console.log('收到API响应:', response)

      if (response.data && response.meta) {
        console.log('解析到的简历数量:', response.data.length)
        const formattedItems = response.data.map(item => formatResumeData(item))
        console.log('格式化后的简历数据:', formattedItems)
        commit('SET_SEARCH_RESULT', {
          items: formattedItems,
          total: response.meta.total
        })
      } else {
        console.warn('API响应格式不正确:', response)
        commit('SET_SEARCH_RESULT', { items: [], total: 0 })
      }
    } catch (error) {
      console.error('搜索简历失败:', error)
      console.error('错误详情:', error.response || error)
      commit('SET_ERROR', error)
      commit('SET_SEARCH_RESULT', { items: [], total: 0 })
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async downloadResume({ commit }, { id, fileName }) {
    try {
      const response = await downloadResume(id)
      const blob = new Blob([response], { type: 'application/octet-stream' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', fileName || `resume_${id}.pdf`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      return true
    } catch (error) {
      commit('SET_ERROR', error)
      throw error
    }
  },

  async toggleResumeStar({ commit }, { id, starred }) {
    try {
      await toggleResumeStar(id, starred)
      commit('UPDATE_RESUME_STAR', { id, starred })
      return true
    } catch (error) {
      commit('SET_ERROR', error)
      throw error
    }
  },

  async exportSearchResult({ commit }, params) {
    try {
      const response = await exportSearchResult(params)
      const blob = new Blob([response], { type: 'application/vnd.ms-excel' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `简历搜索结果_${new Date().toISOString().split('T')[0]}.xlsx`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      return true
    } catch (error) {
      commit('SET_ERROR', error)
      throw error
    }
  },

  async getResumeDetail({ commit }, id) {
    commit('SET_DETAIL_LOADING', true)
    try {
      const response = await getResumeDetail(id)
      if (response) {
        console.log('获取简历详情API响应:', response)
        const formattedDetail = formatResumeData(response)
        console.log('格式化后的简历详情:', formattedDetail)
        commit('SET_CURRENT_DETAIL', formattedDetail)
        return formattedDetail
      }
    } catch (error) {
      console.error('获取简历详情失败:', error)
      commit('SET_ERROR', error)
      throw error
    } finally {
      commit('SET_DETAIL_LOADING', false)
    }
  }
}

const getters = {
  previewUrl: state => state.currentPreviewUrl,
  previewLoading: state => state.previewLoading,
  searchResult: state => state.searchResult,
  loading: state => state.loading,
  error: state => state.error,
  detailLoading: state => state.detailLoading,
  currentDetail: state => state.currentDetail
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
