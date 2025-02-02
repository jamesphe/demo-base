<template>
  <basic-view title="简历上传">
    <div class="upload-container">
      <!-- 上传区域 -->
      <el-upload
        class="upload-area"
        drag
        :action="uploadUrl"
        :before-upload="beforeUpload"
        :on-success="handleSuccess"
        :on-error="handleError"
        :on-progress="handleProgress"
        multiple
        :file-list="fileList"
        :on-remove="handleRemove"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip" slot="tip">
          支持上传PDF、Word、JPG等格式文件，单个文件不超过10MB
        </div>
      </el-upload>

      <!-- 上传列表 -->
      <div class="upload-list" v-if="fileList.length > 0">
        <h3>已上传文件列表</h3>
        <el-table :data="fileList" style="width: 100%">
          <el-table-column prop="name" label="文件名" width="250">
            <template slot-scope="{row}">
              <el-link type="primary" :underline="false" @click="previewFile(row)">
                {{ row.name }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="size" label="大小" width="120">
            <template slot-scope="{row}">
              {{ formatFileSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template slot-scope="{row}">
              <el-tag :type="row.status === 'success' ? 'success' : 'warning'">
                {{ row.status === 'success' ? '上传成功' : '上传中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="上传进度" width="200">
            <template slot-scope="{row}">
              <el-progress 
                v-if="row.status !== 'success'"
                :percentage="row.percentage" 
              />
              <span v-else>完成</span>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template slot-scope="{row}">
              <el-button
                size="mini"
                type="text"
                @click="previewFile(row)"
              >
                预览
              </el-button>
              <el-button
                size="mini"
                type="text"
                @click="handleRemove(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 预览对话框 -->
    <el-dialog
      title="文件预览"
      :visible.sync="previewVisible"
      width="80%"
      :before-close="handlePreviewClose"
    >
      <div class="preview-container" v-loading="previewLoading">
        <iframe v-if="previewUrl" :src="previewUrl" frameborder="0"></iframe>
        <div v-else class="no-preview">
          该文件类型暂不支持预览
        </div>
      </div>
    </el-dialog>
  </basic-view>
</template>

<script>
import BasicView from '@/components/BasicView'

export default {
  name: 'ResumeUpload',
  components: { BasicView },
  data() {
    return {
      uploadUrl: process.env.VUE_APP_BASE_API + '/resume/upload',
      fileList: [],
      previewVisible: false,
      previewUrl: '',
      previewLoading: false
    }
  },
  methods: {
    // 上传前验证
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

    // 验证文件类型
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

    // 上传成功
    handleSuccess(response, file, fileList) {
      this.fileList = fileList
      file.status = 'success'
      this.$message.success('上传成功')
    },

    // 上传失败
    handleError(err, file) {
      this.$message.error('上传失败')
    },

    // 上传进度
    handleProgress(event, file) {
      file.percentage = Math.round(event.percent)
    },

    // 移除文件
    handleRemove(file) {
      const index = this.fileList.indexOf(file)
      if (index !== -1) {
        this.fileList.splice(index, 1)
      }
    },

    // 预览文件
    previewFile(file) {
      this.previewLoading = true
      this.previewVisible = true
      // 这里应该调用后端接口获取预览URL
      this.previewUrl = file.url
      this.previewLoading = false
    },

    // 关闭预览
    handlePreviewClose() {
      this.previewVisible = false
      this.previewUrl = ''
    },

    // 格式化文件大小
    formatFileSize(size) {
      if (size < 1024) {
        return size + ' B'
      } else if (size < 1024 * 1024) {
        return (size / 1024).toFixed(2) + ' KB'
      } else {
        return (size / 1024 / 1024).toFixed(2) + ' MB'
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.upload-container {
  padding: 20px;

  .upload-area {
    width: 100%;
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    text-align: center;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    
    &:hover {
      border-color: #409EFF;
    }
  }

  .upload-list {
    margin-top: 20px;
    
    h3 {
      margin-bottom: 20px;
      font-weight: 500;
      color: #606266;
    }
  }
}

.preview-container {
  height: 70vh;
  
  iframe {
    width: 100%;
    height: 100%;
  }
  
  .no-preview {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #909399;
    font-size: 14px;
  }
}

.el-upload {
  width: 100%;
}

.el-upload-dragger {
  width: 100%;
  height: 200px;
}
</style> 