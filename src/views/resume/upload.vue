<template>
  <basic-view title="简历上传">
    <div class="upload-container">
      <!-- 职位选择 -->
      <div class="position-select">
        <el-form :model="form" label-width="80px">
          <el-form-item label="选择职位">
            <el-select
              v-model="form.positionId"
              placeholder="请选择职位(选填)"
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="item in positions"
                :key="item.id"
                :label="item.title"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <!-- 上传区域 -->
      <div class="upload-wrapper">
        <el-upload
          class="upload-area"
          drag
          action="#"
          :http-request="handleUpload"
          :before-upload="beforeUpload"
          :on-progress="handleProgress"
          multiple
          :file-list="fileList"
          :on-remove="handleRemove"
          :on-exceed="handleExceed"
        >
          <div class="upload-content">
            <div class="upload-icon">
              <i class="el-icon-upload" />
            </div>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <div class="el-upload__tip">
              支持上传PDF、Word、JPG等格式文件，单个文件不超过10MB
            </div>
            <div class="upload-tip">
              <i class="el-icon-info" />
              提示：可同时上传多个文件
            </div>
          </div>
        </el-upload>

        <!-- 文件列表 -->
        <div v-if="fileList.length > 0" class="file-list">
          <div v-for="file in fileList" :key="file.id" class="file-item">
            <div class="file-info">
              <i :class="getFileIcon(file.name)" class="file-icon" />
              <span class="file-name">{{ file.name }}</span>
            </div>
            <div class="file-status">
              <template v-if="file.status === 'uploading'">
                <el-progress
                  :percentage="file.percentage"
                  :stroke-width="2"
                  class="upload-progress"
                />
              </template>
              <template v-else>
                <el-tag
                  :type="getStatusType(file.status)"
                  size="small"
                  class="status-tag"
                >
                  {{ getStatusText(file.status) }}
                </el-tag>
                <el-tag
                  :type="getProcessingStatusType(file.processingStatus)"
                  size="small"
                  class="status-tag"
                >
                  {{ getProcessingStatusText(file.processingStatus) }}
                </el-tag>
              </template>
            </div>
            <div class="file-actions">
              <el-button
                type="text"
                size="mini"
                :disabled="file.status !== 'success'"
                @click="previewFile(file)"
              >
                预览
              </el-button>
              <el-button
                type="text"
                size="mini"
                @click="handleRemove(file)"
              >
                删除
              </el-button>
              <el-button
                v-if="file.processingStatus === 'failed'"
                type="text"
                size="mini"
                @click="retryProcessing(file)"
              >
                重试
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 预览对话框 -->
    <el-dialog
      title="文件预览"
      :visible.sync="previewVisible"
      width="80%"
      :before-close="handlePreviewClose"
      custom-class="preview-dialog"
      top="5vh"
    >
      <div v-loading="previewLoading" class="preview-container">
        <iframe v-if="previewUrl" :src="previewUrl" frameborder="0" />
        <div v-else class="no-preview">
          <i class="el-icon-document" />
          <p>该文件类型暂不支持预览</p>
          <el-button type="primary" size="small" @click="downloadFile">下载文件</el-button>
        </div>
      </div>
    </el-dialog>
  </basic-view>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import BasicView from '@/components/BasicView'

export default {
  name: 'ResumeUpload',
  components: { BasicView },
  data() {
    return {
      fileList: [],
      previewVisible: false,
      previewLoading: false,
      previewUrl: '',
      currentPreviewFile: null,
      form: {
        positionId: null
      }
    }
  },
  computed: {
    ...mapState('resume', ['currentPreviewUrl']),
    ...mapState('position', ['positions'])
  },
  created() {
    this.fetchPositions()
  },
  methods: {
    ...mapActions('resume', [
      'uploadResume',
      'getPreviewUrl',
      'deleteResume',
      'retryResumeProcessing'
    ]),
    ...mapActions('position', ['fetchPositions']),

    beforeUpload(file) {
      const isValidType = this.validateFileType(file.type)
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isValidType) {
        this.$message.error('不支持的文件类型！')
        return false
      }
      if (!isLt10M) {
        this.$message.error('文件大小不能超过 10MB!')
        return false
      }
      return true
    },

    validateFileType(type) {
      const validTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png'
      ]
      return validTypes.includes(type)
    },

    async handleUpload({ file, onProgress }) {
      try {
        const response = await this.uploadResume({
          file,
          positionId: this.form.positionId,
          onProgress
        })
        if (response) {
          this.handleSuccess(response, file)
        }
      } catch (error) {
        this.handleError(error, file)
      }
    },

    handleSuccess(response, file) {
      file.status = 'success'
      this.fileList.push({
        ...file,
        id: response.id,
        url: response.file_path,
        processingStatus: response.processing_status || 'pending'
      })
      this.$message.success('上传成功')

      // 显示上传成功后的操作提示
      this.$notify({
        title: '上传成功',
        message: `文件 "${file.name}" 已成功上传，您可以预览或继续上传更多文件`,
        type: 'success',
        duration: 3000
      })

      // 开始轮询处理状态
      this.pollProcessingStatus(response.id)
    },

    handleError(err, file) {
      file.status = 'error'
      console.error('上传失败:', err)
      this.$message.error('上传失败：' + (err.message || '未知错误'))
    },

    handleProgress(event, file) {
      file.percentage = Math.round(event.percent)
    },

    handleExceed(files, fileList) {
      this.$message.warning(`最多可同时上传 ${fileList.length} 个文件，请先完成当前上传`)
    },

    async handleRemove(file) {
      try {
        if (file.id) {
          await this.deleteResume(file.id)
        }
        const index = this.fileList.indexOf(file)
        if (index !== -1) {
          this.fileList.splice(index, 1)
        }
        this.$message.success('删除成功')
      } catch (error) {
        this.$message.error('删除失败')
      }
    },

    async previewFile(file) {
      if (file.status !== 'success') {
        this.$message.warning('文件尚未上传完成，无法预览')
        return
      }

      this.previewLoading = true
      this.previewVisible = true
      this.currentPreviewFile = file

      try {
        await this.getPreviewUrl(file.id)
        this.previewUrl = this.currentPreviewUrl
      } catch (error) {
        this.$message.error('获取预览失败')
      } finally {
        this.previewLoading = false
      }
    },

    handlePreviewClose() {
      this.previewVisible = false
      this.previewUrl = ''
      this.currentPreviewFile = null
    },

    downloadFile() {
      if (this.currentPreviewFile && this.currentPreviewFile.url) {
        window.open(this.currentPreviewFile.url, '_blank')
      } else {
        this.$message.warning('无法获取文件下载链接')
      }
    },

    clearAllFiles() {
      this.$confirm('确定要清空所有已上传的文件吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 删除所有已上传的文件
        const deletePromises = this.fileList
          .filter(file => file.id)
          .map(file => this.deleteResume(file.id))

        Promise.all(deletePromises)
          .then(() => {
            this.fileList = []
            this.$message.success('已清空所有文件')
          })
          .catch(() => {
            this.$message.error('清空文件失败')
          })
      }).catch(() => {})
    },

    getFileIcon(filename) {
      const ext = filename.split('.').pop().toLowerCase()
      const iconMap = {
        'pdf': 'el-icon-document',
        'doc': 'el-icon-document',
        'docx': 'el-icon-document',
        'jpg': 'el-icon-picture',
        'jpeg': 'el-icon-picture',
        'png': 'el-icon-picture'
      }
      return iconMap[ext] || 'el-icon-document'
    },

    getStatusType(status) {
      const typeMap = {
        'success': 'success',
        'error': 'danger',
        'uploading': 'warning'
      }
      return typeMap[status] || 'info'
    },

    getStatusText(status) {
      const textMap = {
        'success': '上传成功',
        'error': '上传失败',
        'uploading': '上传中'
      }
      return textMap[status] || '未知状态'
    },

    getProcessingStatusType(status) {
      const typeMap = {
        'pending': 'info',
        'processing': 'warning',
        'completed': 'success',
        'failed': 'danger',
        'validation_failed': 'danger'
      }
      return typeMap[status] || 'info'
    },

    getProcessingStatusText(status) {
      const textMap = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '处理完成',
        'failed': '处理失败',
        'validation_failed': '验证失败'
      }
      return textMap[status] || '未知状态'
    },

    async pollProcessingStatus(resumeId) {
      // 模拟轮询处理状态
      // 实际应用中，这里应该调用API获取最新的处理状态
      const file = this.fileList.find(f => f.id === resumeId)
      if (!file) return

      // 模拟处理过程
      setTimeout(() => {
        if (file.processingStatus === 'pending') {
          file.processingStatus = 'processing'
        } else if (file.processingStatus === 'processing') {
          // 随机决定处理结果
          const random = Math.random()
          if (random > 0.2) {
            file.processingStatus = 'completed'
            this.$notify({
              title: '处理完成',
              message: `文件 "${file.name}" 已处理完成`,
              type: 'success',
              duration: 3000
            })
          } else {
            file.processingStatus = 'failed'
            this.$notify({
              title: '处理失败',
              message: `文件 "${file.name}" 处理失败，请重试`,
              type: 'error',
              duration: 3000
            })
          }
        }
      }, 3000)
    },

    async retryProcessing(file) {
      if (!file.id) return

      try {
        this.$message.info('正在重新处理文件...')
        // 使用Vue的响应式系统确保状态更新的原子性
        this.$set(file, 'processingStatus', 'processing')

        // 实际应用中，这里应该调用API重新处理文件
        await this.retryResumeProcessing(file.id)

        // 模拟处理过程
        setTimeout(() => {
          // 使用Vue的响应式系统更新状态
          this.$set(file, 'processingStatus', 'completed')
          this.$notify({
            title: '处理完成',
            message: `文件 "${file.name}" 已重新处理完成`,
            type: 'success',
            duration: 3000
          })
        }, 3000)
      } catch (error) {
        // 使用Vue的响应式系统更新状态
        this.$set(file, 'processingStatus', 'failed')
        this.$message.error('重新处理失败：' + (error.message || '未知错误'))
      }
    },

    formatFileSize(size) {
      if (size < 1024) {
        return size + ' B'
      } else if (size < 1024 * 1024) {
        return (size / 1024).toFixed(2) + ' KB'
      } else {
        return (size / 1024 / 1024).toFixed(2) + ' MB'
      }
    },

    async handleRetry(file) {
      try {
        // 使用Vue的响应式系统确保状态更新的原子性
        this.$set(file, 'processingStatus', 'processing')

        const formData = new FormData()
        formData.append('file', file.raw)
        if (this.repositoryId) {
          formData.append('repository_id', this.repositoryId)
        }
        if (this.jobId) {
          formData.append('job_id', this.jobId)
        }

        const response = await this.$http.post('/api/resumes/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data) {
          // 使用Vue的响应式系统更新状态
          this.$set(file, 'processingStatus', 'success')
          this.$message.success('重新处理成功')

          // 延迟3秒后刷新列表
          setTimeout(() => {
            this.$message({
              message: '正在刷新列表...',
              type: 'success',
              duration: 3000
            })
            this.fetchResumes()
          }, 3000)
        }
      } catch (error) {
        // 使用Vue的响应式系统更新状态
        this.$set(file, 'processingStatus', 'failed')
        this.$message.error('重新处理失败：' + (error.message || '未知错误'))
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.upload-container {
  padding: 24px;
  background: #fff;
  min-height: calc(100vh - 120px);

  .position-select {
    margin-bottom: 24px;

    .el-form-item {
      margin-bottom: 0;
    }
  }

  .upload-wrapper {
    border: 1px dashed #c0c4cc;
    border-radius: 4px;
    padding: 24px;
    background: #fafafa;

    .upload-area {
      width: 100%;

      .upload-content {
        padding: 32px 0;
        text-align: center;

        .upload-icon {
          font-size: 48px;
          color: #909399;
          margin-bottom: 16px;
        }

        .el-upload__text {
          font-size: 16px;
          color: #606266;
          margin-bottom: 12px;

          em {
            color: #409EFF;
            font-style: normal;
            cursor: pointer;
          }
        }

        .el-upload__tip {
          font-size: 13px;
          color: #909399;
          margin-bottom: 8px;
        }

        .upload-tip {
          font-size: 13px;
          color: #909399;

          i {
            margin-right: 4px;
          }
        }
      }
    }

    .file-list {
      margin-top: 24px;
      border-top: 1px solid #ebeef5;
      padding-top: 16px;

      .file-item {
        display: flex;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #ebeef5;

        &:last-child {
          border-bottom: none;
        }

        .file-info {
          flex: 1;
          display: flex;
          align-items: center;
          min-width: 0;

          .file-icon {
            font-size: 16px;
            color: #909399;
            margin-right: 8px;
          }

          .file-name {
            color: #303133;
            font-size: 14px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }

        .file-status {
          width: 240px;
          padding: 0 16px;
          display: flex;
          align-items: center;

          .upload-progress {
            width: 100%;
          }

          .status-tag {
            margin-right: 8px;

            &:last-child {
              margin-right: 0;
            }
          }
        }

        .file-actions {
          width: 180px;
          text-align: right;

          .el-button {
            padding: 0 8px;
          }
        }
      }
    }
  }
}

.preview-dialog {
  .el-dialog__body {
    padding: 0;
  }
}

.preview-container {
  height: 70vh;

  iframe {
    width: 100%;
    height: 100%;
    border: none;
  }

  .no-preview {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #909399;

    i {
      font-size: 48px;
      margin-bottom: 16px;
    }

    p {
      margin-bottom: 16px;
    }
  }
}

// 覆盖 Element UI 默认样式
.el-upload-dragger {
  width: 100%;
  height: auto;
  padding: 0;
  border: none;
  background: none;
}

.el-upload {
  width: 100%;
}
</style>
