<template>
  <basic-view title="简历上传">
    <div class="upload-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h2 class="page-title">简历上传</h2>
        <p class="page-description">您可以在此上传简历文件，我们支持多种格式。上传后系统将自动处理您的简历。</p>
      </div>
      
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
      <div class="upload-section">
        <!-- 文件选择区域 -->
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
            :auto-upload="false"
            :on-change="handleFileChange"
            ref="upload"
          >
            <div class="upload-content">
              <div class="upload-icon">
                <i class="el-icon-upload" />
              </div>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击选择文件</em>
              </div>
              <div class="el-upload__tip animated-tip">
                <i class="el-icon-document"></i>
                支持上传PDF、Word、JPG等格式文件，单个文件不超过10MB
              </div>
              <div class="upload-tip">
                <i class="el-icon-info" />
                提示：可同时上传多个文件
              </div>
              <div class="upload-tip highlight-tip">
                <i class="el-icon-warning" />
                请选择文件后，点击下方"开始上传"按钮
              </div>
            </div>
          </el-upload>
        </div>

        <!-- 上传按钮区域 -->
        <div class="upload-buttons">
          <el-button type="primary" size="large" @click="submitUpload" :loading="uploading" :disabled="!hasFiles" class="pulse-animation">
            <i class="el-icon-upload2"></i> 开始上传
          </el-button>
          <el-button size="large" type="danger" plain @click="clearFiles" :disabled="!hasFiles">
            <i class="el-icon-delete"></i> 清空文件
          </el-button>
        </div>

        <!-- 文件列表 -->
        <div v-if="hasFiles" class="file-list">
          <div class="file-list-header">已选择的文件</div>
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
      },
      uploading: false
    }
  },
  computed: {
    ...mapState('resume', ['currentPreviewUrl']),
    ...mapState('position', ['positions']),
    hasFiles() {
      return this.fileList && this.fileList.length > 0;
    }
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
      // 首先检查是否已经上传过
      const existingFile = this.fileList.find(f => 
        f.uid === file.uid && f.status === 'success');
      
      if (existingFile) {
        console.log('文件已上传过，跳过上传', file.name);
        return;
      }

      if (!this.form.positionId) {
        try {
          await this.$confirm('您尚未选择职位，确定要继续上传吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          });
        } catch (error) {
          // 用户点击取消
          return;
        }
      }

      try {
        // 更新文件状态为上传中
        const fileIndex = this.fileList.findIndex(f => f.uid === file.uid);
        if (fileIndex > -1) {
          this.$set(this.fileList[fileIndex], 'status', 'uploading');
          this.$set(this.fileList[fileIndex], 'processingStatus', 'pending');
        }

        const response = await this.uploadResume({
          file,
          positionId: this.form.positionId,
          onProgress
        });
        
        if (response) {
          this.handleSuccess(response, file);
        }
      } catch (error) {
        this.handleError(error, file);
      } finally {
        // 确保上传完成后，无论成功失败都设置uploading为false
        if (this.fileList.every(f => f.status !== 'uploading')) {
          this.uploading = false;
        }
      }
    },

    handleSuccess(response, file) {
      // 找到对应的文件
      const fileIndex = this.fileList.findIndex(f => f.uid === file.uid);
      if (fileIndex > -1) {
        // 使用Vue的响应式系统更新状态
        this.$set(this.fileList[fileIndex], 'status', 'success');
        this.$set(this.fileList[fileIndex], 'id', response.id);
        this.$set(this.fileList[fileIndex], 'url', response.file_path);
        this.$set(this.fileList[fileIndex], 'processingStatus', response.processing_status || 'pending');
        
        this.$message.success('上传成功');

        // 显示上传成功后的操作提示
        this.$notify({
          title: '上传成功',
          message: `文件 "${file.name}" 已成功上传`,
          type: 'success',
          duration: 3000
        });

        // 开始轮询处理状态
        this.pollProcessingStatus(response.id);
        
        // 检查是否所有文件都已上传完成
        this.checkUploadingStatus();
      } else {
        console.error('找不到要更新的文件:', file.name);
      }
    },

    handleError(err, file) {
      // 找到对应的文件
      const fileIndex = this.fileList.findIndex(f => f.uid === file.uid);
      if (fileIndex > -1) {
        // 使用Vue的响应式系统更新状态
        this.$set(this.fileList[fileIndex], 'status', 'error');
      }
      console.error('上传失败:', err);
      this.$message.error('上传失败：' + (err.message || '未知错误'));
      
      // 检查是否所有文件都已上传完成
      this.checkUploadingStatus();
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

    clearFiles() {
      this.$refs.upload.clearFiles()
      this.fileList = []
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
      // 找到对应的文件
      const fileIndex = this.fileList.findIndex(f => f.id === resumeId);
      if (fileIndex === -1) return;

      // 模拟处理过程
      setTimeout(() => {
        const file = this.fileList[fileIndex];
        if (!file) return; // 文件可能已被删除

        if (file.processingStatus === 'pending') {
          this.$set(this.fileList[fileIndex], 'processingStatus', 'processing');
          // 继续轮询
          setTimeout(() => this.pollProcessingStatus(resumeId), 2000);
        } else if (file.processingStatus === 'processing') {
          // 随机决定处理结果
          const random = Math.random();
          if (random > 0.2) {
            this.$set(this.fileList[fileIndex], 'processingStatus', 'completed');
            this.$notify({
              title: '处理完成',
              message: `文件 "${file.name}" 已处理完成`,
              type: 'success',
              duration: 3000
            });
          } else {
            this.$set(this.fileList[fileIndex], 'processingStatus', 'failed');
            this.$notify({
              title: '处理失败',
              message: `文件 "${file.name}" 处理失败，请重试`,
              type: 'error',
              duration: 3000
            });
          }
        }
      }, 2000);
    },

    async retryProcessing(file) {
      if (!file.id) return;

      try {
        this.$message.info('正在重新处理文件...');
        
        // 找到对应的文件
        const fileIndex = this.fileList.findIndex(f => f.id === file.id);
        if (fileIndex > -1) {
          // 使用Vue的响应式系统更新状态
          this.$set(this.fileList[fileIndex], 'processingStatus', 'processing');
        }

        await this.retryResumeProcessing(file.id);

        // 模拟处理过程
        setTimeout(() => {
          const fileIndex = this.fileList.findIndex(f => f.id === file.id);
          if (fileIndex > -1) {
            // 使用Vue的响应式系统更新状态
            this.$set(this.fileList[fileIndex], 'processingStatus', 'completed');
            this.$notify({
              title: '处理完成',
              message: `文件 "${file.name}" 已重新处理完成`,
              type: 'success',
              duration: 3000
            });
          }
        }, 3000);
      } catch (error) {
        const fileIndex = this.fileList.findIndex(f => f.id === file.id);
        if (fileIndex > -1) {
          // 使用Vue的响应式系统更新状态
          this.$set(this.fileList[fileIndex], 'processingStatus', 'failed');
        }
        this.$message.error('重新处理失败：' + (error.message || '未知错误'));
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

    async submitUpload() {
      if (!this.form.positionId) {
        try {
          await this.$confirm('您尚未选择职位，确定要继续上传吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          })
        } catch (error) {
          return;
        }
      }

      if (this.fileList.length === 0) {
        this.$message.warning('请先选择要上传的文件');
        return;
      }

      this.uploading = true;
      try {
        // 使用 Element UI 的上传组件的 submit 方法
        this.$refs.upload.submit();
        // 注意：实际上传会由handleUpload方法处理
      } catch (error) {
        this.uploading = false;
        this.$message.error('上传失败：' + (error.message || '未知错误'));
      }
    },

    handleFileChange(file, fileList) {
      // 将el-upload的fileList同步到组件的fileList
      // 保留已有的状态信息
      this.fileList = fileList.map(f => {
        const existingFile = this.fileList.find(ef => ef.uid === f.uid);
        if (existingFile) {
          return {
            ...f,
            id: existingFile.id,
            status: existingFile.status,
            processingStatus: existingFile.processingStatus,
            url: existingFile.url
          };
        }
        // 为新添加的文件设置初始状态
        return {
          ...f,
          processingStatus: 'pending'
        };
      });
      console.log('文件列表更新:', this.fileList.length);
    },

    // 检查是否所有文件都已完成上传
    checkUploadingStatus() {
      // 如果没有文件正在上传中，将uploading设为false
      if (!this.fileList.some(file => file.status === 'uploading')) {
        this.uploading = false;
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
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

  .page-header {
    text-align: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid #ebeef5;
    
    .page-title {
      font-size: 28px;
      color: #303133;
      margin-bottom: 10px;
      font-weight: 500;
    }
    
    .page-description {
      font-size: 16px;
      color: #606266;
      max-width: 800px;
      margin: 0 auto;
      line-height: 1.6;
    }
  }

  .position-select {
    margin-bottom: 30px;
    max-width: 800px;
    margin: 0 auto 30px;

    .el-form-item {
      margin-bottom: 0;
    }
  }

  /* 固定上传按钮样式 */
  .fixed-buttons {
    max-width: 800px;
    margin: 0 auto 20px;
    text-align: center;
    padding: 20px;
    background-color: #f0f9eb;
    border: 1px solid #e1f3d8;
    border-radius: 4px;

    .el-button {
      margin: 0 10px;
      padding: 12px 30px;
      font-size: 16px;
      
      i {
        margin-right: 5px;
      }
    }
  }

  .upload-section {
    max-width: 800px;
    margin: 0 auto;
    
    .upload-wrapper {
      border: 1px dashed #c0c4cc;
      border-radius: 8px;
      background: #f9fafc;
      padding: 30px;
      margin-bottom: 30px;
      transition: all 0.3s;
      
      &:hover {
        border-color: #409EFF;
        background: #f0f7ff;
        box-shadow: 0 0 10px rgba(64, 158, 255, 0.1);
      }

      .upload-area {
        width: 100%;

        .upload-content {
          padding: 40px 0;
          text-align: center;

          .upload-icon {
            font-size: 64px;
            color: #409EFF;
            margin-bottom: 20px;
            transition: transform 0.3s;
            animation: float 3s ease-in-out infinite;
            
            &:hover {
              transform: scale(1.1);
            }
          }

          .el-upload__text {
            font-size: 18px;
            color: #606266;
            margin-bottom: 16px;

            em {
              color: #409EFF;
              font-style: normal;
              cursor: pointer;
              font-weight: bold;
              text-decoration: underline;
              transition: color 0.3s;
              
              &:hover {
                color: #66b1ff;
              }
            }
          }

          .el-upload__tip {
            font-size: 14px;
            color: #909399;
            margin-bottom: 12px;
          }
          
          .animated-tip {
            animation: fadeIn 0.5s ease-in-out;
            padding: 8px 16px;
            background-color: #f0f7ff;
            border-radius: 4px;
            display: inline-block;
            margin: 10px auto;
            border-left: 3px solid #409EFF;
            
            i {
              margin-right: 6px;
              color: #409EFF;
            }
          }

          .upload-tip {
            font-size: 14px;
            color: #909399;
            line-height: 1.5;
            margin-top: 8px;

            i {
              margin-right: 4px;
            }
          }
          
          .highlight-tip {
            color: #e6a23c;
            margin-top: 15px;
            padding: 8px 16px;
            background-color: #fdf6ec;
            border-radius: 4px;
            border-left: 3px solid #e6a23c;
            display: inline-block;
            font-weight: 500;
            
            i {
              color: #e6a23c;
            }
          }
        }
      }
    }

    .upload-buttons {
      text-align: center;
      margin: 30px 0;
      padding: 20px;
      background-color: #f0f9eb;
      border: 1px solid #e1f3d8;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      
      .el-button {
        margin: 0 10px;
        padding: 15px 40px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 6px;
        transition: all 0.3s;
        
        &:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        i {
          margin-right: 8px;
        }
      }
      
      .pulse-animation:not(:disabled) {
        animation: pulse 2s infinite;
      }
    }

    .file-list {
      background: #fff;
      border-radius: 8px;
      border: 1px solid #ebeef5;
      margin-top: 20px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
      overflow: hidden;
      animation: slideDown 0.5s ease-in-out;

      .file-list-header {
        padding: 16px 20px;
        font-size: 16px;
        font-weight: 500;
        color: #303133;
        border-bottom: 1px solid #ebeef5;
        background: #f5f7fa;
        border-radius: 8px 8px 0 0;
      }

      .file-item {
        display: flex;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid #ebeef5;
        transition: background-color 0.3s;
        animation: fadeIn 0.5s ease-in-out;

        &:hover {
          background-color: #f5f7fa;
        }

        &:last-child {
          border-bottom: none;
        }

        .file-info {
          flex: 1;
          display: flex;
          align-items: center;
          min-width: 0;

          .file-icon {
            font-size: 24px;
            color: #909399;
            margin-right: 12px;
          }

          .file-name {
            color: #303133;
            font-size: 14px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-weight: 500;
          }
        }

        .file-status {
          width: 240px;
          padding: 0 20px;
          display: flex;
          align-items: center;

          .upload-progress {
            width: 100%;
          }

          .status-tag {
            margin-right: 8px;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;

            &:last-child {
              margin-right: 0;
            }
          }
        }

        .file-actions {
          width: 120px;
          text-align: right;

          .el-button {
            padding: 6px 10px;
            transition: all 0.3s;
            
            &:hover {
              color: #409EFF;
              background: #ecf5ff;
              border-radius: 4px;
            }
          }
        }
      }
    }
  }
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
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

.el-select {
  .el-input__inner {
    border-radius: 6px;
  }
}

.el-form-item__label {
  font-weight: 500;
}
</style>
