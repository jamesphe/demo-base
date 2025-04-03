<template>
  <basic-view title="简历解析">
    <div class="parse-container">
      <!-- 解析列表 -->
      <el-table v-loading="loading" :data="parseList" style="width: 100%">
        <el-table-column prop="fileName" label="文件名" width="200" />
        <el-table-column label="关联职位" width="180">
          <template slot-scope="{row}">
            <el-tag v-if="row.jobTitle" size="small">{{ row.jobTitle }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="候选人信息" width="200">
          <template slot-scope="{row}">
            <div v-if="row.name" class="candidate-info">
              <span>{{ row.name }}</span>
              <el-tag size="mini" type="info" class="ml-5">
                {{ row.phone || row.email || '-' }}
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
        <el-table-column label="匹配度" width="100">
          <template slot-scope="{row}">
            <el-progress
              v-if="row.matchingScore"
              :percentage="row.matchingScore"
              :color="getMatchingColor"
            />
            <span v-else>-</span>
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
              type="text"
              :disabled="row.parseStatus === 'parsing'"
              @click="handleParse(row)"
            >
              {{ row.parseStatus === 'failed' ? '重新解析' : '解析' }}
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
        <div v-loading="resultLoading">
          <!-- 基本信息卡片 -->
          <el-card class="info-card" shadow="hover">
            <div slot="header" class="card-header">
              <span><i class="el-icon-user" /> 基本信息</span>
            </div>
            <div v-if="currentResult && Object.keys(currentResult).length" class="resume-info">
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="info-item">
                    <label>姓名：</label>
                    {{ currentResult.name || '-' }}
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <label>性别：</label>
                    {{ currentResult.gender === 'F' ? '女' : '男' }}
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <label>年龄：</label>
                    {{ currentResult.age || '28' }} 岁
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <label>电话：</label>
                    {{ currentResult.phone || '-' }}
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <label>邮箱：</label>
                    {{ currentResult.email || '-' }}
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <label>工作年限：</label>
                    {{ currentResult.experienceYears ? `${currentResult.experienceYears}年` : '-' }}
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <label>最高学历：</label>
                    {{ currentResult.highestEducation || '-' }}
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <label>专业：</label>
                    {{ currentResult.major || '-' }}
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-item">
                    <label>英语水平：</label>
                    {{ currentResult.englishLevel || '-' }}
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-card>

          <!-- 求职意向卡片 -->
          <el-card class="info-card" shadow="hover">
            <div slot="header" class="card-header">
              <span><i class="el-icon-aim" /> 求职意向</span>
            </div>
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="info-item">
                  <label>期望职位：</label>
                  {{ currentResult.expectedPosition || '-' }}
                </div>
              </el-col>
              <el-col :span="8">
                <div class="info-item">
                  <label>期望地点：</label>
                  {{ currentResult.expectedLocation || '-' }}
                </div>
              </el-col>
              <el-col :span="8">
                <div class="info-item">
                  <label>当前职位：</label>
                  {{ currentResult.currentPosition || '-' }}
                </div>
              </el-col>
              <el-col :span="8">
                <div class="info-item">
                  <label>当前公司：</label>
                  {{ currentResult.currentCompany || '-' }}
                </div>
              </el-col>
            </el-row>
          </el-card>

          <!-- 技能特长 -->
          <template v-if="currentResult && currentResult.skills && currentResult.skills.length">
            <el-card class="info-card skill-list" shadow="hover">
              <div slot="header" class="card-header">
                <span><i class="el-icon-medal" /> 技能特长</span>
              </div>
              <el-row :gutter="20">
                <el-col v-for="(skill, index) in currentResult.skills" :key="index" :span="24">
                  <div class="skill-item">
                    <h4>
                      {{ skill.name || '-' }}
                      <el-tag v-if="skill.level" size="small" :type="getSkillTagType(skill.level)">
                        {{ skill.level }}
                      </el-tag>
                    </h4>
                    <p>{{ skill.description || '-' }}</p>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </template>

          <!-- 工作经历 -->
          <template v-if="currentResult && currentResult.workHistory && currentResult.workHistory.length">
            <el-card class="info-card" shadow="hover">
              <div slot="header" class="card-header">
                <span><i class="el-icon-office-building" /> 工作经历</span>
              </div>
              <el-timeline>
                <el-timeline-item
                  v-for="(work, index) in currentResult.workHistory"
                  :key="index"
                  :timestamp="formatWorkPeriod(work.startDate, work.endDate)"
                  placement="top"
                  type="primary"
                >
                  <el-card shadow="never" class="timeline-card">
                    <h4>{{ work.company || '-' }} - {{ work.position || '-' }}</h4>
                    <p class="work-description">{{ work.description || '-' }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-card>
          </template>
        </div>
      </el-dialog>
    </div>
  </basic-view>
</template>

<script>
import BasicView from '@/components/BasicView'
import { getParseList, parseResume, getParseResult, deleteParseRecord } from '@/api/resume'

export default {
  name: 'ResumeParse',
  components: {
    BasicView
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
      ]
    }
  },
  computed: {
    getMatchingColor() {
      return (percentage) => {
        for (const item of this.matchingColors) {
          if (percentage <= item.percentage) {
            return item.color
          }
        }
        return '#409EFF'
      }
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
            jobTitle: item.jobTitle || item.job_title,
            candidateName: item.candidateName || item.candidate_name,
            candidatePhone: item.candidatePhone || item.candidate_phone,
            candidateEmail: item.candidateEmail || item.candidate_email,
            matchingScore: item.matchingScore || item.matching_score
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
      this.resultVisible = true
      this.resultLoading = true
      try {
        const response = await getParseResult(row.id)
        // 处理工作经历中的公司名称
        if (response.work_history) {
          response.work_history = response.work_history.map(work => ({
            ...work,
            company: work.company || '未提供'
          }))
        }
        this.currentResult = response || {}
      } catch (error) {
        console.error('获取解析结果失败:', error)
        this.$message.error('获取解析结果失败')
        this.currentResult = {}
      } finally {
        this.resultLoading = false
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

        await parseResume(row.fileUrl)

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
      this.currentResult = {}
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
</style>
