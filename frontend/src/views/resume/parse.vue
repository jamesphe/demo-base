<template>
  <basic-view title="简历解析">
    <div class="parse-container">
      <!-- 解析列表 -->
      <el-table v-loading="loading" :data="parseList" style="width: 100%">
        <el-table-column prop="fileName" label="文件名" min-width="250">
          <template slot-scope="{row}">
            <div class="file-name-cell">
              <el-link
                type="primary"
                :underline="false"
                class="resume-name"
                @click="handlePreviewResume(row)"
              >
                {{ row.fileName }}
              </el-link>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="候选人信息" width="200">
          <template slot-scope="{row}">
            <div v-if="row.name" class="candidate-info">
              <span>{{ row.name }}</span>
              <el-tag size="mini" type="info" class="ml-5">
                {{ row.phone || row.email || '-' }}
              </el-tag>
              <el-tag v-if="row.expectedPosition" size="mini" type="success" class="ml-5">
                {{ row.expectedPosition }}
              </el-tag>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="uploadTime" label="上传时间" width="180">
          <template slot-scope="{row}">
            {{ formatDate(row.uploadTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="parseStatus" label="解析状态" width="100">
          <template slot-scope="{row}">
            <el-tag :type="getStatusType(row.parseStatus)">
              {{ getStatusText(row.parseStatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="解析结果">
          <template slot-scope="{row}">
            <el-button
              type="text"
              :disabled="row.parseStatus !== 'success'"
              @click="showParseResult(row)"
            >
              查看结果
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template slot-scope="{row}">
            <el-button
              v-if="row.parseStatus === 'failed' || row.parseStatus === 'pending'"
              type="text"
              @click="handleParse(row)"
            >
              解析
            </el-button>
            <el-button
              v-if="row.parseStatus === 'parsing'"
              type="text"
              disabled
            >
              解析中
            </el-button>
            <el-button
              type="text"
              class="delete-btn"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 添加分页组件 -->
      <div class="pagination-container">
        <el-pagination
          background
          :current-page="listQuery.page"
          :page-sizes="[10, 20, 30, 50]"
          :page-size="listQuery.limit"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 解析结果对话框 -->
      <el-dialog
        title="解析结果"
        :visible.sync="resultVisible"
        width="70%"
        custom-class="resume-dialog"
        @close="handleDialogClose"
      >
        <resume-detail
          :detail="currentDetail"
          :loading="detailLoading"
        />
      </el-dialog>

      <!-- 使用新的简历预览组件 -->
      <resume-preview
        :visible.sync="resumePreviewVisible"
        :resume-id="currentPreviewId"
        :file-name="currentPreviewFileName"
        @close="handlePreviewClose"
      />
    </div>
  </basic-view>
</template>

<script>
import BasicView from '@/components/BasicView'
import ResumeDetail from '@/components/ResumeDetail'
import ResumePreview from '@/components/ResumePreview'
import { getParseList, parseResume, deleteParseRecord } from '@/api/resume'
import { mapGetters } from 'vuex'

export default {
  name: 'ResumeParse',
  components: {
    BasicView,
    ResumeDetail,
    ResumePreview
  },
  data() {
    return {
      loading: false,
      parseList: [],
      resultVisible: false,
      resultLoading: false,
      currentResult: {},
      listQuery: {
        page: 1,
        limit: 10
      },
      total: 0,
      matchingColors: [
        { color: '#F56C6C', percentage: 60 },
        { color: '#E6A23C', percentage: 75 },
        { color: '#67C23A', percentage: 90 },
        { color: '#409EFF', percentage: 100 }
      ],
      // 简历预览相关
      resumePreviewVisible: false,
      currentPreviewId: null,
      currentPreviewFileName: ''
    }
  },
  computed: {
    ...mapGetters('resume', [
      'currentDetail',
      'detailLoading',
      'previewUrl',
      'previewLoading'
    ]),
    getMatchingColor() {
      return (percentage) => {
        for (const item of this.matchingColors) {
          if (percentage <= item.percentage) {
            return item.color
          }
        }
        return '#409EFF'
      }
    },
    baseApiUrl() {
      return process.env.VUE_APP_BASE_API || ''
    },
    authToken() {
      return getToken()
    }
  },
  created() {
    this.getParseList()
  },
  methods: {
    // 获取解析列表
    async getParseList() {
      this.loading = true
      try {
        console.log('开始获取解析列表...')
        const res = await getParseList({
          page: this.listQuery.page,
          limit: this.listQuery.limit
        })
        console.log('获取解析列表响应:', res)

        // 处理返回的数据
        if (res.data) {
          // 如果是数组格式
          const items = Array.isArray(res.data) ? res.data : (res.data.items || [])

          this.parseList = items.map(item => ({
            id: item.id,
            fileName: item.fileName || item.file_name,
            fileUrl: item.fileUrl || item.file_path,
            uploadTime: item.uploadTime || item.createdAt || item.created_at,
            parseStatus: this.normalizeStatus(item.processingStatus || item.processing_status),
            parsedData: item.parsedData || item.parsed_data,
            jobTitle: item.expected_position,
            name: item.name,
            phone: item.phone,
            email: item.email,
            matchingScore: item.matching_score,
            expectedPosition: item.expected_position,
            expectedLocation: item.expected_location,
            currentPosition: item.current_position,
            currentCompany: item.current_company,
            highestEducation: item.highest_education,
            major: item.major,
            experienceYears: item.experience_years,
            englishLevel: item.english_level,
            skills: item.skills,
            workHistory: item.work_history,
            eduExperience: item.edu_experience
          }))

          // 更新总数
          this.total = res.meta?.total || res.data?.total || items.length
        } else {
          this.parseList = []
          this.total = 0
        }
      } catch (error) {
        console.error('获取解析列表失败:', error)
        this.$message.error('获取列表失败')
      } finally {
        this.loading = false
        console.log('获取解析列表完成')
      }
    },

    // 添加新方法用于标准化状态
    normalizeStatus(status) {
      const statusMap = {
        'completed': 'success',
        'processing': 'parsing',
        'failed': 'failed',
        'pending': 'pending'
      }
      return statusMap[status] || 'pending'
    },

    // 格式化日期
    formatDate(date) {
      return new Date(date).toLocaleString()
    },

    // 获取状态类型
    getStatusType(status) {
      const types = {
        success: 'success',
        parsing: 'warning',
        failed: 'danger',
        pending: 'info'
      }
      return types[status] || 'info'
    },

    // 获取状态文本
    getStatusText(status) {
      const texts = {
        success: '解析成功',
        parsing: '解析中',
        failed: '解析失败',
        pending: '待解析'
      }
      return texts[status] || '未知状态'
    },

    // 显示解析结果
    async showParseResult(row) {
      console.log('显示简历解析结果:', row)
      this.resultVisible = true
      try {
        await this.$store.dispatch('resume/getResumeDetail', row.id)
        console.log('简历详情获取成功')
      } catch (error) {
        console.error('获取解析结果失败:', error)
        this.$message.error('获取解析结果失败')
      }
    },

    // 解析简历
    async handleParse(row) {
      try {
        await this.$confirm('确认解析该简历?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        // 创建一个新对象来追踪状态
        const updatedRow = { ...row }
        updatedRow.parseStatus = 'parsing'
        Object.assign(row, updatedRow)

        await parseResume(row.id)

        updatedRow.parseStatus = 'success'
        Object.assign(row, updatedRow)

        this.$message.success('解析成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('解析失败')
          const updatedRow = { ...row }
          updatedRow.parseStatus = 'failed'
          Object.assign(row, updatedRow)
        }
      }
    },

    // 删除简历
    async handleDelete(row) {
      try {
        await this.$confirm('确认删除该简历?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await deleteParseRecord(row.id)
        const index = this.parseList.indexOf(row)
        this.parseList.splice(index, 1)
        this.$message.success('删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
        }
      }
    },

    // 添加处理页码改变的方法
    handleCurrentChange(page) {
      this.listQuery.page = page
      this.getParseList()
    },

    // 添加处理每页条数改变的方法
    handleSizeChange(limit) {
      this.listQuery.limit = limit
      this.listQuery.page = 1
      this.getParseList()
    },

    // 处理对话框关闭
    handleDialogClose() {
      this.$store.commit('resume/SET_CURRENT_DETAIL', null)
    },

    // 获取技能标签类型
    getSkillTagType(level) {
      if (!level) return ''
      const typeMap = {
        '熟练': 'success',
        '良好': 'primary',
        '熟悉': 'warning',
        '懂技术': 'info',
        '经常关注': ''
      }
      return typeMap[level] || ''
    },

    // 格式化工作时间段
    formatWorkPeriod(startDate, endDate) {
      if (!startDate) return '-'
      const formatDate = date => {
        try {
          return new Date(date).toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'numeric'
          })
        } catch (error) {
          console.error('日期格式化错误:', error)
          return date
        }
      }
      const start = formatDate(startDate)
      const end = endDate ? formatDate(endDate) : '至今'
      return `${start} - ${end}`
    },

    // 格式化教育时间段
    formatEduPeriod(startDate, endDate) {
      if (!startDate) return '-'
      const formatDate = date => {
        try {
          return new Date(date).toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'numeric'
          })
        } catch (error) {
          console.error('日期格式化错误:', error)
          return date
        }
      }
      const start = formatDate(startDate)
      const end = endDate ? formatDate(endDate) : '至今'
      return `${start} - ${end}`
    },

    // 预览简历 - 使用新组件
    async handlePreviewResume(row) {
      try {
        // 先尝试获取预览URL，确认简历存在
        await this.$store.dispatch('resume/getPreviewUrl', row.id)
        
        // 如果没有抛出错误，则简历存在，可以打开预览窗口
        this.currentPreviewId = row.id
        this.currentPreviewFileName = row.fileName
        this.resumePreviewVisible = true
      } catch (error) {
        // 如果获取URL失败，提示用户简历不存在
        console.error('简历预览失败:', error)
        this.$message.error('该简历无法预览')
        // 不打开预览窗口
      }
    },
    
    // 处理预览关闭
    handlePreviewClose() {
      this.currentPreviewId = null
      this.currentPreviewFileName = ''
    },

    getFileType(fileName) {
      if (!fileName) return ''
      const extension = fileName.split('.').pop().toLowerCase()
      return extension
    },

    async previewWordDocument(row) {
      try {
        // 发起下载请求获取文件内容
        const response = await fetch(`${this.baseApiUrl}/resume/download/${row.id}`, {
          headers: {
            'Authorization': `${this.authToken}`
          }
        })
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const blob = await response.blob()
        
        // 检查文件类型
        const fileType = this.getFileType(row.fileName)
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
        
        // 设置下载URL
        const cleanToken = this.authToken && this.authToken.startsWith('Bearer ') ? this.authToken.substring(7) : this.authToken
        this.downloadUrl = `${this.baseApiUrl}/resume/download/${row.id}?token=${cleanToken}`
      } catch (error) {
        console.error('Word文档预览失败:', error)
        this.$message.error('文档预览失败：' + error.message)
        throw error
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
    },

    handlePreviewError(e) {
      console.error('预览加载失败:', e)
      this.$message.error('预览加载失败，请尝试直接下载文件')
    },

    toggleFullscreen() {
      this.isFullscreen = !this.isFullscreen
    }
  }
}
</script>

<style lang="scss" scoped>
.parse-container {
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.section-title {
  margin: 20px 0;
  padding-left: 10px;
  font-size: 16px;
  font-weight: 500;
  border-left: 4px solid #409EFF;
  background-color: #f5f7fa;
  line-height: 40px;
  padding: 0 15px;
}

.delete-btn {
  color: #F56C6C;
}

.resume-dialog {
  .el-dialog__body {
    padding: 20px;
  }
}

.info-card {
  margin-bottom: 20px;

  &:last-child {
    margin-bottom: 0;
  }

  .card-header {
    display: flex;
    align-items: center;

    i {
      margin-right: 8px;
      font-size: 18px;
      color: #409EFF;
    }

    span {
      font-size: 16px;
      font-weight: 500;
    }
  }
}

.resume-info {
  padding: 20px;

  .info-item {
    margin-bottom: 15px;
    display: flex;
    align-items: center;

    &:last-child {
      margin-bottom: 0;
    }

    label {
      min-width: 80px;
      color: #606266;
      font-weight: 500;
      margin-right: 10px;
    }

    &-content {
      color: #303133;
    }
  }
}

.skill-list {
  margin-bottom: 20px;

  .skill-item {
    padding: 15px 0;
    border-bottom: 1px solid #eee;

    &:last-child {
      border-bottom: none;
      padding-bottom: 0;
    }

    h4 {
      margin: 0 0 10px;
      display: flex;
      align-items: center;
      font-size: 15px;
      color: #303133;

      .el-tag {
        margin-left: 10px;
      }
    }

    p {
      margin: 0;
      color: #666;
      line-height: 1.6;
      text-align: justify;
    }
  }
}

.timeline-card {
  background-color: #f9fafc;

  h4 {
    margin: 0 0 10px;
    color: #303133;
    font-size: 15px;
    font-weight: 500;
  }
}

.work-description {
  white-space: pre-line;
  line-height: 1.6;
  color: #666;
  text-align: justify;
}

.candidate-info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;

  .ml-5 {
    margin-left: 5px;
  }
}

.el-progress {
  margin: 8px 0;
}

.file-name-cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resume-preview-dialog {
  .dialog-custom-header {
    display: flex;
    align-items: center;
    
    i {
      font-size: 18px;
      color: #606266;
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        color: #409EFF;
        transform: scale(1.1);
      }
    }
    
    .header-actions {
      margin-left: auto;
      display: flex;
      gap: 16px;
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
