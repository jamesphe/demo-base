<template>
  <el-dialog
    :visible.sync="dialogVisible"
    :width="isFullscreen ? '100%' : '80%'"
    :close-on-click-modal="false"
    :fullscreen="isFullscreen"
    class="resume-preview-dialog"
    append-to-body
    destroy-on-close
    @open="handleDialogOpen"
    @close="handleDialogClose"
  >
    <div slot="title" class="dialog-custom-header">
      <i class="el-icon-document" />
      <span>简历预览</span>
      <div class="header-actions">
        <el-tooltip content="全屏查看" placement="bottom" :enterable="false">
          <div class="action-button">
            <i
              :class="['el-icon-full-screen', { 'is-fullscreen': isFullscreen }]"
              @click="toggleFullscreen"
            />
          </div>
        </el-tooltip>
        <el-tooltip content="下载原文件" placement="bottom" :enterable="false">
          <div class="action-button">
            <i class="el-icon-download" @click="handleDownload" />
          </div>
        </el-tooltip>
      </div>
    </div>
    <div v-loading="isLoading" class="preview-container">
      <template v-if="isDocPreview">
        <div class="doc-preview" v-html="previewContent" />
      </template>
      <template v-else>
        <iframe
          v-if="previewUrl"
          :src="completePreviewUrl"
          class="preview-object"
          frameborder="0"
          style="width: 100%; height: calc(100vh - 200px); min-height: 500px;"
          @load="handlePreviewLoad"
          @error="handlePreviewError"
        />
        <div v-else class="no-preview">
          <i class="el-icon-document-delete" style="font-size: 48px; color: #909399; margin-bottom: 16px;" />
          <p>暂无可预览的文件</p>
        </div>
      </template>
    </div>
  </el-dialog>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import mammoth from 'mammoth'
import { getToken } from '@/utils/auth'

export default {
  name: 'ResumePreview',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    resumeId: {
      type: [String, Number],
      default: null
    },
    fileName: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      isFullscreen: false,
      previewContent: '',
      isDocPreview: false,
      downloadUrl: '',
      localPreviewLoading: false
    }
  },
  computed: {
    ...mapGetters('resume', [
      'previewUrl',
      'previewLoading'
    ]),
    baseApiUrl() {
      return process.env.VUE_APP_BASE_API || ''
    },
    authToken() {
      return getToken()
    },
    dialogVisible: {
      get() {
        return this.visible
      },
      set(val) {
        this.$emit('update:visible', val)
      }
    },
    isLoading() {
      return this.previewLoading || this.localPreviewLoading
    },
    completePreviewUrl() {
      if (!this.previewUrl) return ''
      
      // 确保使用正确的URL格式
      const url = this.previewUrl.startsWith('http') 
        ? this.previewUrl 
        : `${this.baseApiUrl}${this.previewUrl}`
        
      // 添加token
      const token = this.authToken
      const cleanToken = token && token.startsWith('Bearer ') ? token.substring(7) : token
      const separator = url.includes('?') ? '&' : '?'
      
      return cleanToken ? `${url}${separator}token=${cleanToken}` : url
    }
  },
  watch: {
    async resumeId(newVal) {
      if (newVal && this.dialogVisible) {
        await this.loadPreview()
      }
    },
    async visible(newVal) {
      if (newVal && this.resumeId) {
        await this.loadPreview()
      }
    }
  },
  methods: {
    ...mapActions('resume', [
      'getPreviewUrl'
    ]),
    
    async loadPreview() {
      if (!this.resumeId) return
      
      try {
        console.log('开始预览简历:', this.resumeId)
        this.localPreviewLoading = true
        this.isDocPreview = false
        this.previewContent = ''

        // 获取文件类型
        const fileType = this.getFileType(this.fileName)

        if (fileType === 'doc' || fileType === 'docx') {
          // 处理doc/docx文件预览
          this.isDocPreview = true
          await this.previewWordDocument()
        } else {
          // 处理其他类型文件预览
          console.log('正在获取预览URL...')
          await this.getPreviewUrl(this.resumeId)
          
          const token = this.authToken
          // 确保令牌不包含Bearer前缀
          const cleanToken = token && token.startsWith('Bearer ') ? token.substring(7) : token
          const tokenParam = cleanToken ? `?token=${cleanToken}` : ''
          
          // 检查API返回的previewUrl并使用正确的下载路径
          console.log('Store中的预览URL:', this.previewUrl)
          
          // 从store获取的预览URL可能是相对路径，需要拼接baseApiUrl
          if (this.previewUrl) {
            // 提取路径中的关键部分
            const urlPath = this.previewUrl.includes('/resumes/') 
              ? `/resumes/${this.resumeId}/download` 
              : `/resume/download/${this.resumeId}`
              
            this.downloadUrl = `${this.baseApiUrl}${urlPath}${tokenParam}`
          } else {
            // 使用默认下载URL格式
            this.downloadUrl = `${this.baseApiUrl}/resume/download/${this.resumeId}${tokenParam}`
          }
          
          console.log('下载URL:', this.downloadUrl)
        }
      } catch (error) {
        console.error('获取简历预览失败:', error)
        this.$message.error('获取简历预览失败')
      } finally {
        this.localPreviewLoading = false
      }
    },

    getFileType(fileName) {
      if (!fileName) return ''
      const extension = fileName.split('.').pop().toLowerCase()
      return extension
    },

    async previewWordDocument() {
      try {
        this.localPreviewLoading = true
        
        // 确定正确的API路径
        const apiPath = `/resumes/${this.resumeId}/download`
        console.log('请求Word文档路径:', `${this.baseApiUrl}${apiPath}`)
        
        // 发起下载请求获取文件内容
        const response = await fetch(`${this.baseApiUrl}${apiPath}`, {
          headers: {
            'Authorization': `${this.authToken}`
          }
        })
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const blob = await response.blob()
        
        // 检查文件类型
        const fileType = this.getFileType(this.fileName)
        if (fileType !== 'doc' && fileType !== 'docx') {
          throw new Error('不支持的文件格式')
        }
        
        // 读取文件内容
        const arrayBuffer = await blob.arrayBuffer()
        
        // 使用mammoth.js转换docx为HTML
        const result = await mammoth.convertToHtml(
          { arrayBuffer },
          {
            convertImage: mammoth.images.imgElement(function(image) {
              return image.read('base64').then(function(imageBase64) {
                return {
                  src: `data:${image.contentType};base64,${imageBase64}`
                }
              })
            })
          }
        )
        this.previewContent = result.value
        
        // 设置下载URL（使用相同的路径）
        const cleanToken = this.authToken && this.authToken.startsWith('Bearer ') ? this.authToken.substring(7) : this.authToken
        this.downloadUrl = `${this.baseApiUrl}${apiPath}?token=${cleanToken}`
      } catch (error) {
        console.error('Word文档预览失败:', error)
        this.$message.error('文档预览失败：' + error.message)
      } finally {
        this.localPreviewLoading = false
      }
    },

    handleDownload() {
      if (this.downloadUrl) {
        console.log('开始下载文件:', this.downloadUrl)
        window.open(this.downloadUrl, '_blank')
      } else {
        this.$message.warning('下载URL不存在')
      }
    },

    handlePreviewLoad() {
      console.log('预览加载成功')
      this.localPreviewLoading = false
    },

    handlePreviewError(e) {
      console.error('预览加载失败:', e)
      this.$message.error('预览加载失败，请尝试直接下载文件')
      this.localPreviewLoading = false
    },

    toggleFullscreen() {
      this.isFullscreen = !this.isFullscreen
    },
    
    handleDialogOpen() {
      if (this.resumeId) {
        this.loadPreview()
      }
    },
    
    handleDialogClose() {
      this.isFullscreen = false
      this.previewContent = ''
      this.isDocPreview = false
      this.$emit('close')
    }
  }
}
</script>

<style lang="scss" scoped>
.resume-preview-dialog {
  ::v-deep .el-dialog__header {
    padding: 15px 20px;
    border-bottom: 1px solid #e4e7ed;
    margin-right: 0;
  }
  
  ::v-deep .el-dialog__headerbtn {
    top: 15px;
    right: 15px;
    font-size: 18px;
    z-index: 10;
  }
  
  .dialog-custom-header {
    display: flex;
    align-items: center;
    
    i {
      font-size: 20px;
      color: #409EFF;
      margin-right: 10px;
    }
    
    span {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
    
    .header-actions {
      margin-left: auto;
      display: flex;
      align-items: center;
      
      .action-button {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 32px;
        height: 32px;
        border-radius: 4px;
        margin-left: 8px;
        background-color: #f5f7fa;
        cursor: pointer;
        transition: all 0.3s;
        
        i {
          margin-right: 0;
          font-size: 18px;
          color: #606266;
          transition: all 0.3s;
        }
        
        &:hover {
          background-color: #ecf5ff;
          
          i {
            color: #409EFF;
            transform: scale(1.1);
          }
        }
        
        .is-fullscreen {
          color: #409EFF;
        }
      }
    }
  }
  
  .preview-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f5f7fa;
    overflow: hidden;
    
    .preview-object {
      width: 100%;
      height: 100%;
      border: none;
      background: white;
    }
    
    .doc-preview {
      width: 100%;
      height: calc(100vh - 200px);
      min-height: 500px;
      padding: 20px;
      background: white;
      overflow-y: auto;
      box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
      border-radius: 4px;
      
      ::v-deep {
        h1, h2, h3, h4, h5, h6 {
          margin: 1em 0 0.5em;
          color: #303133;
        }
        
        p {
          margin: 0.5em 0;
          line-height: 1.6;
          color: #606266;
        }
        
        img {
          max-width: 100%;
          height: auto;
          margin: 1em 0;
        }
        
        table {
          width: 100%;
          border-collapse: collapse;
          margin: 1em 0;
          
          th, td {
            border: 1px solid #dcdfe6;
            padding: 8px;
            text-align: left;
          }
          
          th {
            background-color: #f5f7fa;
            color: #606266;
          }
        }
        
        ul, ol {
          padding-left: 2em;
          margin: 0.5em 0;
        }
        
        li {
          line-height: 1.6;
          color: #606266;
        }
      }
    }
    
    .no-preview {
      text-align: center;
      color: #909399;
      font-size: 14px;
    }
  }
}
</style> 