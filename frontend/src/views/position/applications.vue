<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>职位申请管理</span>
      </div>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="申请状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="已审核" value="reviewed" />
            <el-option label="已面试" value="interviewed" />
            <el-option label="已录用" value="offered" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已撤回" value="withdrawn" />
          </el-select>
        </el-form-item>
        <el-form-item label="职位名称">
          <el-input v-model="searchForm.jobTitle" placeholder="请输入职位名称" clearable />
        </el-form-item>
        <el-form-item label="候选人">
          <el-input v-model="searchForm.candidateName" placeholder="请输入候选人姓名" clearable />
        </el-form-item>
        <el-form-item label="学历要求">
          <el-select v-model="searchForm.education" placeholder="请选择学历" clearable>
            <el-option label="大专" value="college" />
            <el-option label="本科" value="bachelor" />
            <el-option label="硕士" value="master" />
            <el-option label="博士" value="phd" />
          </el-select>
        </el-form-item>
        <el-form-item label="工作年限">
          <el-select v-model="searchForm.experience" placeholder="请选择工作年限" clearable>
            <el-option label="应届生" value="fresh" />
            <el-option label="1年以下" value="0-1" />
            <el-option label="1-3年" value="1-3" />
            <el-option label="3-5年" value="3-5" />
            <el-option label="5-10年" value="5-10" />
            <el-option label="10年以上" value="10+" />
          </el-select>
        </el-form-item>
        <el-form-item label="匹配度">
          <el-select v-model="searchForm.matchScore" placeholder="请选择匹配度" clearable>
            <el-option label="优秀(80分以上)" value="80+" />
            <el-option label="良好(60-80分)" value="60-80" />
            <el-option label="一般(60分以下)" value="0-60" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请时间">
          <el-date-picker
            v-model="searchForm.applyTimeRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 批量操作工具栏 -->
      <div v-if="selectedApplications.length > 0" class="batch-operations">
        <el-button-group>
          <el-button size="small" type="primary" @click="handleBatchUpdateStatus('reviewed')">批量标记为已审核</el-button>
          <el-button size="small" type="success" @click="handleBatchUpdateStatus('interviewed')">批量标记为已面试</el-button>
          <el-button size="small" type="warning" @click="handleBatchUpdateStatus('rejected')">批量标记为已拒绝</el-button>
        </el-button-group>
        <span class="selected-count">已选择 {{ selectedApplications.length }} 项</span>
      </div>

      <!-- 申请列表 -->
      <el-table
        v-loading="loading"
        :data="applicationList"
        element-loading-text="加载中..."
        border
        fit
        highlight-current-row
        class="application-table"
        @sort-change="handleSortChange"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <!-- 申请ID列 -->
        <el-table-column
          label="申请ID"
          prop="id"
          align="center"
          width="80"
          class-name="id-column"
          sortable="custom"
        />

        <!-- 职位名称列 -->
        <el-table-column
          label="职位名称"
          prop="job_title"
          align="center"
          min-width="180"
          class-name="job-column"
          sortable="custom"
        >
          <template slot-scope="scope">
            <el-link
              type="primary"
              :underline="false"
              class="job-title"
              @click="handleViewJob(scope.row.job)"
            >
              <span v-if="scope.row.job">
                {{ scope.row.job.title }}
              </span>
              <span v-else>-</span>
            </el-link>
          </template>
        </el-table-column>

        <!-- 候选人列 -->
        <el-table-column
          label="候选人"
          prop="candidate_name"
          align="center"
          min-width="120"
          class-name="candidate-column"
          sortable="custom"
        >
          <template slot-scope="scope">
            <div class="candidate-info">
              <span class="candidate-name">{{ scope.row.candidateName || '未知' }}</span>
              <el-tag
                v-if="scope.row.resumeHighestEducation"
                size="mini"
                type="info"
              >{{ scope.row.resumeHighestEducation }}</el-tag>
            </div>
          </template>
        </el-table-column>

        <!-- 简历名称列 -->
        <el-table-column
          label="简历名称"
          prop="resume_name"
          align="center"
          min-width="180"
          class-name="resume-column"
          show-overflow-tooltip
          sortable="custom"
        >
          <template slot-scope="scope">
            <el-link
              type="primary"
              :underline="false"
              class="resume-name"
              @click="handlePreviewResume(scope.row)"
            >{{ scope.row.resumeName || '' }}</el-link>
          </template>
        </el-table-column>

        <!-- 工作年限列 -->
        <el-table-column
          label="工作年限"
          prop="experience_years"
          align="center"
          width="100"
          class-name="experience-column"
          sortable="custom"
        >
          <template slot-scope="{row}">
            <span class="experience-years">
              {{ row.resumeExperienceYears ? row.resumeExperienceYears + '年' : '未知' }}
            </span>
          </template>
        </el-table-column>

        <!-- 申请时间列 -->
        <el-table-column
          label="申请时间"
          prop="apply_time"
          align="center"
          width="160"
          class-name="time-column"
          sortable="custom"
        >
          <template slot-scope="scope">
            <span class="apply-time">{{ formatDateTime(scope.row.applyTime) }}</span>
          </template>
        </el-table-column>

        <!-- 状态列 -->
        <el-table-column
          label="状态"
          prop="status"
          align="center"
          width="100"
          class-name="status-column"
          sortable="custom"
        >
          <template slot-scope="scope">
            <el-tag
              :type="getStatusType(scope.row.status)"
              :class="['status-tag', scope.row.status]"
              effect="light"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 匹配度列 -->
        <el-table-column
          label="匹配度"
          prop="match_score"
          align="center"
          width="120"
          class-name="match-column"
          sortable="custom"
        >
          <template slot-scope="{row}">
            <div class="match-score-wrapper">
              <el-progress
                :percentage="row.matchScore || 0"
                :color="getMatchScoreColor(row.matchScore)"
                :stroke-width="14"
                class="match-progress"
              />
              <el-button
                v-if="row.matchReason"
                type="text"
                class="match-reason-btn"
                @click="showMatchReason(row)"
              >
                <i class="el-icon-info" />
              </el-button>
            </div>
          </template>
        </el-table-column>

        <!-- 操作列 -->
        <el-table-column
          label="操作"
          align="center"
          width="160"
          fixed="right"
          class-name="action-column"
          header-align="center"
        >
          <template slot-scope="scope">
            <div class="action-buttons">
              <el-button
                size="mini"
                type="primary"
                plain
                class="action-btn"
                @click="handleView(scope.row)"
              >
                <i class="el-icon-view" />查看
              </el-button>
              <el-button
                size="mini"
                type="success"
                plain
                :disabled="scope.row.status === 'withdrawn'"
                class="action-btn"
                @click="handleUpdateStatus(scope.row)"
              >
                <i class="el-icon-edit" />更新
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <pagination
        v-show="total>0"
        :total="total"
        :page.sync="listQuery.page"
        :limit.sync="listQuery.limit"
        @pagination="getList"
      />
    </el-card>

    <!-- 状态更新对话框 -->
    <el-dialog title="更新申请状态" :visible.sync="statusDialogVisible">
      <el-form :model="statusForm" label-width="100px">
        <el-form-item label="申请状态">
          <el-select v-model="statusForm.status" placeholder="请选择状态">
            <el-option label="待处理" value="pending" />
            <el-option label="已审核" value="reviewed" />
            <el-option label="已面试" value="interviewed" />
            <el-option label="已录用" value="offered" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核备注">
          <el-input
            v-model="statusForm.reviewNotes"
            type="textarea"
            :rows="3"
            placeholder="请输入审核备注"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="statusDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitStatusUpdate">确 定</el-button>
      </div>
    </el-dialog>

    <!-- 匹配度分析对话框 -->
    <el-dialog
      title="匹配度分析"
      :visible.sync="matchReasonDialogVisible"
      width="900px"
      class="match-reason-dialog"
      :close-on-click-modal="false"
    >
      <div class="match-analysis">
        <div class="match-score">
          <el-progress
            type="circle"
            :percentage="currentMatchScore"
            :color="getMatchScoreColor(currentMatchScore)"
          />
          <div class="score-text">匹配度评分</div>
          <div class="score-level">
            {{ getMatchLevel(currentMatchScore) }}
          </div>
        </div>
        <div class="match-details">
          <el-tabs type="border-card">
            <el-tab-pane label="教育背景匹配">
              <div class="match-section" v-html="getFormattedSection('教育背景与要求的匹配度')" />
            </el-tab-pane>
            <el-tab-pane label="工作经验匹配">
              <div class="match-section" v-html="getFormattedSection('工作经验与要求的匹配度')" />
            </el-tab-pane>
            <el-tab-pane label="技能要求匹配">
              <div class="match-section" v-html="getFormattedSection('技能与岗位要求的匹配度')" />
            </el-tab-pane>
            <el-tab-pane label="求职意向匹配">
              <div class="match-section" v-html="getFormattedSection('求职意向与职位条件的匹配度')" />
            </el-tab-pane>
            <el-tab-pane label="薪资匹配">
              <div class="match-section" v-html="getFormattedSection('薪资期望的匹配度')" />
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-dialog>

    <!-- 简历详情弹窗 -->
    <el-dialog
      title="简历详情"
      :visible.sync="resumeDetailVisible"
      width="70%"
      custom-class="resume-dialog"
      @close="handleResumeDialogClose"
    >
      <resume-detail
        :detail="formatResumeDetail"
        :loading="resumeDetailLoading"
      />
    </el-dialog>

    <!-- 简历预览弹窗 -->
    <resume-preview
      :visible.sync="resumePreviewVisible"
      :resume-id="currentPreviewId"
      :file-name="currentPreviewFileName"
      @close="handlePreviewClose"
    />

    <!-- 职位详情弹窗 -->
    <el-dialog
      title="职位详情"
      :visible.sync="jobDetailVisible"
      width="65%"
      class="job-detail-dialog"
    >
      <div v-loading="jobDetailLoading">
        <el-card class="box-card">
          <div slot="header" class="card-header">
            <span>基本信息</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="info-item">
                <label>职位名称：</label>
                {{ currentJob.title || '-' }}
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <label>职位类型：</label>
                <el-tag :type="currentJob.type === 'fulltime' ? 'primary' : currentJob.type === 'parttime' ? 'success' : 'warning'">
                  {{ currentJob.type === 'fulltime' ? '全职' : currentJob.type === 'parttime' ? '兼职' : '实习' }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <label>所属部门：</label>
                {{ currentJob.department || '-' }}
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <label>工作地点：</label>
                {{ currentJob.location || '-' }}
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <label>薪资范围：</label>
                <span class="salary-text">{{ currentJob.salaryMin }}-{{ currentJob.salaryMax }}K/{{ currentJob.salaryUnit === 'month' ? '月' : '年' }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <label>招聘人数：</label>
                {{ currentJob.headcount || '-' }} 人
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card class="box-card">
          <div slot="header" class="card-header">
            <span>要求与职责</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="info-item">
                <label>学历要求：</label>
                <el-tag size="mini" type="info">
                  {{ getEducationText(currentJob.educationRequired) }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <label>经验要求：</label>
                {{ currentJob.experienceRequired || '-' }}
              </div>
            </el-col>
          </el-row>
          <div class="info-section">
            <h4>职位描述</h4>
            <p class="description-text">{{ currentJob.description || '-' }}</p>
          </div>
          <div class="info-section">
            <h4>任职要求</h4>
            <p class="description-text">{{ currentJob.requirements || '-' }}</p>
          </div>
        </el-card>

        <el-card v-if="currentJob.benefits && currentJob.benefits.length" class="box-card">
          <div slot="header" class="card-header">
            <span>福利待遇</span>
          </div>
          <div class="benefits-list">
            <el-tag
              v-for="(benefit, index) in currentJob.benefits"
              :key="index"
              size="small"
              type="success"
              effect="plain"
              class="benefit-tag"
            >
              {{ getBenefitLabel(benefit) }}
            </el-tag>
          </div>
        </el-card>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import Pagination from '@/components/Pagination'
import { getToken } from '@/utils/auth'
import ResumeDetail from '@/components/ResumeDetail'
import ResumePreview from '@/components/ResumePreview'

export default {
  name: 'PositionApplications',
  components: {
    Pagination,
    ResumeDetail,
    ResumePreview
  },
  data() {
    return {
      listQuery: {
        page: 1,
        limit: 10,
        sortField: '',
        sortOrder: ''
      },
      searchForm: {
        status: '',
        jobTitle: '',
        candidateName: '',
        education: '',
        experience: '',
        matchScore: '',
        applyTimeRange: []
      },
      statusDialogVisible: false,
      statusForm: {
        id: null,
        status: '',
        reviewNotes: ''
      },
      matchReasonDialogVisible: false,
      currentMatchReason: '',
      currentMatchScore: 0,
      resumeDetailVisible: false,
      resumeDetailLoading: false,
      currentResume: null,
      resumePreviewVisible: false,
      currentPreviewId: null,
      currentPreviewFileName: '',
      jobDetailVisible: false,
      jobDetailLoading: false,
      currentJob: {},
      selectedApplications: []
    }
  },
  computed: {
    ...mapGetters('jobApplication', [
      'applicationList',
      'total',
      'loading'
    ]),
    ...mapGetters('resume', [
      'previewUrl',
      'previewLoading',
      'currentDetail'
    ]),
    ...mapGetters('position', [
      'currentPosition',
      'loading'
    ]),
    baseApiUrl() {
      return process.env.VUE_APP_BASE_API || ''
    },
    authToken() {
      return getToken()
    },
    formatResumeDetail() {
      return this.currentDetail || {}
    }
  },
  created() {
    this.getList()
  },
  methods: {
    ...mapActions('jobApplication', [
      'getApplicationList',
      'updateStatus'
    ]),
    ...mapActions('resume', [
      'getPreviewUrl',
      'getResumeDetail'
    ]),
    ...mapActions('position', [
      'getPositionDetail'
    ]),
    async getList() {
      try {
        const params = {
          ...this.listQuery,
          ...this.searchForm,
          applyTimeStart: this.searchForm.applyTimeRange?.[0],
          applyTimeEnd: this.searchForm.applyTimeRange?.[1]
        }

        // 处理匹配度筛选
        if (this.searchForm.matchScore) {
          const [min, max] = this.searchForm.matchScore.split('-')
          if (max) {
            params.matchScoreMin = parseInt(min)
            params.matchScoreMax = parseInt(max)
          } else {
            params.matchScoreMin = parseInt(min.replace('+', ''))
          }
        }

        // 重命名参数以匹配后端API
        if (params.jobTitle) {
          params.job_title = params.jobTitle
          delete params.jobTitle
        }
        if (params.candidateName) {
          params.candidate_name = params.candidateName
          delete params.candidateName
        }
        if (params.matchScore) {
          params.match_score = params.matchScore
          delete params.matchScore
        }
        if (params.applyTimeStart) {
          params.apply_time_start = params.applyTimeStart
          delete params.applyTimeStart
        }
        if (params.applyTimeEnd) {
          params.apply_time_end = params.applyTimeEnd
          delete params.applyTimeEnd
        }
        if (params.sortField) {
          params.sort_field = params.sortField
          delete params.sortField
        }
        if (params.sortOrder) {
          params.sort_order = params.sortOrder
          delete params.sortOrder
        }

        console.log('Fetching applications with params:', params)
        const result = await this.getApplicationList(params)
        console.log('API result:', result)
      } catch (error) {
        console.error('获取申请列表失败:', error)
        this.$message.error('获取申请列表失败')
      }
    },
    handleSearch() {
      this.listQuery.page = 1
      this.getList()
    },
    resetSearch() {
      this.searchForm = {
        status: '',
        jobTitle: '',
        candidateName: '',
        education: '',
        experience: '',
        matchScore: '',
        applyTimeRange: []
      }
      this.listQuery.page = 1
      this.getList()
    },
    getStatusType(status) {
      const statusMap = {
        pending: 'info',
        reviewed: 'warning',
        interviewed: 'warning',
        offered: 'success',
        rejected: 'danger',
        withdrawn: ''
      }
      return statusMap[status]
    },
    getStatusText(status) {
      const statusMap = {
        pending: '待处理',
        reviewed: '已审核',
        interviewed: '已面试',
        offered: '已录用',
        rejected: '已拒绝',
        withdrawn: '已撤回'
      }
      return statusMap[status]
    },
    getMatchScoreColor(score) {
      if (score >= 80) return '#67C23A'
      if (score >= 60) return '#E6A23C'
      return '#F56C6C'
    },
    handleView(row) {
      this.resumeDetailVisible = true
      this.resumeDetailLoading = true
      this.getResumeDetails(row.resumeId)
    },
    handleUpdateStatus(row) {
      this.statusForm.id = row.id
      this.statusForm.status = row.status
      this.statusForm.reviewNotes = row.reviewNotes || ''
      this.statusDialogVisible = true
    },
    async submitStatusUpdate() {
      try {
        await this.updateStatus({
          id: this.statusForm.id,
          data: {
            status: this.statusForm.status,
            reviewNotes: this.statusForm.reviewNotes
          }
        })
        this.$message.success('状态更新成功')
        this.statusDialogVisible = false
      } catch (error) {
        console.error('更新状态失败:', error)
        this.$message.error('更新状态失败')
      }
    },
    formatDateTime(timestamp) {
      if (!timestamp) return '暂无数据'
      try {
        const date = new Date(timestamp)
        if (isNaN(date.getTime())) return '数据格式错误'

        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')

        return `${year}-${month}-${day} ${hours}:${minutes}`
      } catch (error) {
        console.error('日期格式化错误:', error)
        return '格式化错误'
      }
    },
    showMatchReason(row) {
      this.currentMatchReason = row.matchReason
      this.currentMatchScore = row.matchScore || 0
      this.matchReasonDialogVisible = true
    },
    getMatchLevel(score) {
      if (score >= 80) return '匹配度优秀'
      if (score >= 70) return '匹配度良好'
      if (score >= 60) return '基本匹配'
      return '匹配度较低'
    },
    getFormattedSection(sectionTitle) {
      if (!this.currentMatchReason) return ''

      // 将内容按数字序号分段
      const sections = {}
      const matches = this.currentMatchReason.match(/(\d+)\.\s+(.*?)(?=\d+\.|$)/gs)

      if (!matches) return ''

      matches.forEach(section => {
        const [, num, content] = section.match(/(\d+)\.\s+(.*)$/s) || []
        if (num && content) {
          sections[content.split('：')[0]] = content.split('：')[1]?.trim()
        }
      })

      // 获取对应章节的内容
      const sectionKey = Object.keys(sections).find(key =>
        key.includes(sectionTitle.replace(/[：:]\s*$/, '').replace(/与要求的匹配度$/, ''))
      )

      if (!sectionKey || !sections[sectionKey]) return ''

      // 格式化内容
      return sections[sectionKey]
        .replace(/\n/g, '<br>')
        .replace(/。/g, '。<br><br>') // 在句号后添加双换行
        .replace(/；/g, '；<br>') // 在分号后添加换行
        .replace(/，/g, '，<span class="text-space"></span>') // 在逗号后添加空格
        .replace(/：/g, '：<span class="text-space"></span>') // 在冒号后添加空格
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/^\s*[-*+]\s(.*)$/gm, '<li>$1</li>')
        .replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>')
    },
    async getResumeDetails(resumeId) {
      try {
        console.log('Fetching resume details for ID:', resumeId)
        const result = await this.getResumeDetail(resumeId)
        console.log('Resume details API response:', result)

        this.currentResume = result
        console.log('Current resume state after update:', this.currentResume)

        // 检查关键数据是否存在
        console.log('Resume data check:', {
          hasBasicInfo: !!this.currentResume,
          name: this.currentResume?.name,
          skills: this.currentResume?.skills,
          workHistory: this.currentResume?.workHistory,
          education: this.currentResume?.highestEducation
        })
      } catch (error) {
        console.error('获取简历详情失败:', error)
        console.error('Error details:', error.response?.data || error.message)
        this.$message.error('获取简历详情失败')
      } finally {
        this.resumeDetailLoading = false
        console.log('Resume detail loading finished')
      }
    },
    handleResumeDialogClose() {
      this.currentResume = null
    },
    getSkillTagType(level) {
      const typeMap = {
        '熟练': 'success',
        '良好': 'primary',
        '熟悉': 'warning',
        '懂技术': 'info'
      }
      return typeMap[level] || ''
    },
    formatWorkPeriod(startDate, endDate) {
      if (!startDate) return '-'
      const formatDate = date => {
        return new Date(date).toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: 'numeric'
        })
      }
      const start = formatDate(startDate)
      const end = endDate ? formatDate(endDate) : '至今'
      return `${start} - ${end}`
    },
    async handlePreviewResume(row) {
      try {
        console.log('开始预览简历:', row)
        console.log('简历ID:', row.resumeId)
        
        if (!row.resumeId) {
          console.error('简历ID不存在')
          this.$message.error('无法预览简历：简历ID不存在')
          return
        }
        
        this.currentPreviewId = row.resumeId
        this.currentPreviewFileName = row.resumeName || 'resume.pdf'
        this.resumePreviewVisible = true
      } catch (error) {
        console.error('预览简历失败:', error)
        this.$message.error('预览简历失败')
      }
    },
    handlePreviewClose() {
      this.currentPreviewId = null
      this.currentPreviewFileName = ''
    },
    async handleViewJob(job) {
      console.log('handleViewJob called with job:', job)
      if (!job) {
        console.warn('No job data provided')
        return
      }
      this.jobDetailVisible = true
      this.jobDetailLoading = true
      try {
        // 通过 store 获取职位详情
        const jobDetail = await this.getPositionDetail(job.id)
        console.log('Job detail from API:', jobDetail)
        // 转换数据格式
        this.currentJob = {
          title: jobDetail.title,
          type: jobDetail.jobType,
          department: jobDetail.department,
          location: jobDetail.location,
          salaryMin: jobDetail.salaryMin,
          salaryMax: jobDetail.salaryMax,
          salaryUnit: jobDetail.salaryType === '月薪' ? 'month' : 'year',
          description: jobDetail.description,
          requirements: jobDetail.requirements,
          benefits: jobDetail.benefits ? jobDetail.benefits.split(',') : [],
          experienceRequired: jobDetail.experienceRequired,
          educationRequired: jobDetail.educationRequired,
          headcount: jobDetail.headcount || 1
        }
        console.log('Transformed job data:', this.currentJob)
      } catch (error) {
        console.error('Error fetching job detail:', error)
        this.$message.error('获取职位详情失败')
      } finally {
        this.jobDetailLoading = false
      }
    },
    getEducationText(education) {
      const educationMap = {
        'bachelor': '本科',
        'master': '硕士',
        'phd': '博士',
        'college': '大专',
        'highschool': '高中',
        'other': '其他'
      }
      return educationMap[education?.toLowerCase()] || education || '-'
    },
    getBenefitLabel(value) {
      const benefitMap = {
        'insurance': '五险一金',
        'annual_bonus': '年终奖',
        'overtime_pay': '加班补助',
        'meal': '餐补',
        'transportation': '交通补助',
        'communication': '通讯补贴',
        'holiday_benefits': '节日福利',
        'paid_leave': '带薪年假',
        'health_check': '定期体检',
        'travel': '员工旅游'
      }
      return benefitMap[value] || value
    },
    handleSortChange({ prop, order }) {
      this.listQuery.sortField = prop
      this.listQuery.sortOrder = order === 'ascending' ? 'asc' : order === 'descending' ? 'desc' : ''
      this.getList()
    },
    handleSelectionChange(selection) {
      this.selectedApplications = selection
    },
    async handleBatchUpdateStatus(status) {
      if (this.selectedApplications.length === 0) {
        this.$message.warning('请先选择要操作的申请')
        return
      }

      try {
        await this.$confirm(
          `确认将选中的 ${this.selectedApplications.length} 条申请标记为"${this.getStatusText(status)}"?`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        const promises = this.selectedApplications.map(application =>
          this.updateStatus({
            id: application.id,
            data: {
              status: status,
              reviewNotes: `批量更新状态为${this.getStatusText(status)}`
            }
          })
        )

        await Promise.all(promises)
        this.$message.success('批量更新状态成功')
        this.selectedApplications = []
        this.getList()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量更新状态失败:', error)
          this.$message.error('批量更新状态失败')
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.application-table {
  margin-top: 20px;
  border-radius: 4px;

  ::v-deep {
    .el-table__header-wrapper {
      th.el-table__cell {
        background-color: #f5f7fa;
        color: #606266;
        font-weight: 600;
        height: 50px;
        border-right: 1px solid #ebeef5;
        border-bottom: 1px solid #ebeef5;
        padding: 0 !important;

        .cell {
          white-space: nowrap;
          line-height: 50px;
          padding: 0 12px;
          display: flex;
          align-items: center;
          justify-content: center;

          .caret-wrapper {
            margin-left: 4px;
            height: 50px;
            display: flex;
            align-items: center;
          }
        }

        &.is-leaf {
          border-bottom: 1px solid #ebeef5;
        }

        &:last-child {
          border-right: none;
        }
      }
    }

    .el-table__fixed-right {
      height: 100% !important;
      background-color: #fff;

      .el-table__fixed-header-wrapper {
        th.el-table__cell {
          background-color: #f5f7fa;
          color: #606266;
          font-weight: 600;
          height: 50px;
          border-right: 1px solid #ebeef5;
          border-bottom: 1px solid #ebeef5;
          padding: 0 !important;

          .cell {
            white-space: nowrap;
            line-height: 50px;
            padding: 0 12px;
            display: flex;
            align-items: center;
            justify-content: center;

            .caret-wrapper {
              margin-left: 4px;
              height: 50px;
              display: flex;
              align-items: center;
            }
          }
        }
      }
    }
  }

  .candidate-info {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;

    .candidate-name {
      font-weight: 500;
    }

    .el-tag {
      transform: scale(0.9);
    }
  }

  .job-title {
    color: #409EFF;
    font-weight: 500;
  }

  .resume-name {
    font-size: 13px;
  }

  .experience-years {
    color: #606266;
  }

  .apply-time {
    color: #909399;
    font-size: 13px;
  }

  .status-tag {
    text-align: center;
    min-width: 65px;

    &.pending { background-color: #f4f4f5; }
    &.reviewed { background-color: #fdf6ec; }
    &.interviewed { background-color: #ecf5ff; }
    &.offered { background-color: #f0f9eb; }
    &.rejected { background-color: #fef0f0; }
    &.withdrawn { background-color: #f4f4f5; color: #909399; }
  }

  .match-score-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;

    .match-progress {
      width: 85%;
    }

    .match-reason-btn {
      padding: 2px;

      .el-icon-info {
        font-size: 16px;
        color: #909399;
        transition: color 0.2s;

        &:hover {
          color: #409EFF;
        }
      }
    }
  }

  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 8px;

    .action-btn {
      padding: 5px 8px;

      i {
        margin-right: 3px;
        font-size: 14px;
      }
    }
  }
}

.match-reason-dialog {
  ::v-deep .el-dialog__body {
    padding: 24px;
  }

  .match-analysis {
    display: flex;
    gap: 24px;

    .match-score {
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
      background: #f8f9fa;
      border-radius: 8px;
      width: 180px;

      .el-progress {
        width: 140px;
        height: 140px;
      }

      .score-text {
        margin-top: 16px;
        font-size: 16px;
        color: #606266;
      }

      .score-level {
        margin-top: 8px;
        font-size: 14px;
        color: #909399;
        padding: 4px 12px;
        background: #ecf5ff;
        border-radius: 12px;
      }
    }

    .match-details {
      flex-grow: 1;
      min-width: 0;

      ::v-deep .el-tabs {
        box-shadow: none;

        .el-tabs__header {
          margin-bottom: 0;

          .el-tabs__item {
            height: 40px;
            line-height: 40px;
            font-size: 14px;

            &.is-active {
              font-weight: 600;
            }
          }
        }

        .el-tabs__content {
          padding: 20px;
          background: #fff;
          border-radius: 0 0 4px 4px;

          .match-section {
            color: #606266;
            line-height: 1.8;
            font-size: 14px;
            padding: 16px;
            background: #fafafa;
            border-radius: 4px;
            letter-spacing: 0.5px;

            br {
              margin: 8px 0;

              & + br {
                margin-top: -4px;
              }
            }

            .text-space {
              width: 0.3em;
            }

            strong {
              padding: 2px 6px;
            }

            em {
              font-style: normal;
              color: #409EFF;
            }

            code {
              margin: 0 2px;
              padding: 3px 8px;
              background: #f5f7fa;
              border-radius: 4px;
              color: #476582;
              font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
              font-size: 13px;
            }

            ul {
              margin: 12px 0;
              padding: 12px 12px 12px 24px;
              background: #fff;
              border-radius: 4px;
              box-shadow: 0 2px 4px rgba(0,0,0,0.05);

              li {
                margin-bottom: 12px;
                position: relative;
                padding-left: 4px;

                &::before {
                  content: '';
                  position: absolute;
                  left: -16px;
                  top: 10px;
                  width: 6px;
                  height: 6px;
                  border-radius: 50%;
                  background-color: #409EFF;
                  opacity: 0.7;
                }

                &:last-child {
                  margin-bottom: 0;
                }
              }
            }
          }
        }
      }
    }
  }
}

// 优化进度条颜色
::v-deep .el-progress__text {
  color: #303133;
  font-weight: 600;
}

::v-deep .el-dialog {
  border-radius: 8px;
  overflow: hidden;

  .el-dialog__header {
    margin: 0;
    padding: 20px 30px;
    border-bottom: 1px solid #e4e7ed;
    background: #fff;

    .el-dialog__title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }

  .el-dialog__headerbtn {
    top: 20px;
    right: 20px;
  }

  @media screen and (max-width: 1200px) {
    width: 95% !important;
    margin: 0 auto;
  }
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
  .info-item {
    margin-bottom: 15px;
    display: flex;
    align-items: center;

    label {
      min-width: 80px;
      color: #606266;
      font-weight: 500;
      margin-right: 10px;
    }
  }
}

.skill-list {
  .skill-item {
    padding: 15px 0;
    border-bottom: 1px solid #eee;

    &:last-child {
      border-bottom: none;
    }

    h4 {
      margin: 0 0 10px;
      display: flex;
      align-items: center;
      font-size: 15px;

      .el-tag {
        margin-left: 10px;
      }
    }

    p {
      margin: 0;
      color: #666;
      line-height: 1.6;
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
}

.job-detail-dialog {
  .box-card {
    margin-bottom: 20px;
    border-radius: 8px;

    .card-header {
      display: flex;
      align-items: center;
      font-size: 16px;
      font-weight: 500;
    }
  }

  .info-item {
    margin-bottom: 15px;
    display: flex;
    align-items: center;

    label {
      min-width: 80px;
      color: #606266;
      font-weight: 500;
      margin-right: 10px;
    }
  }

  .info-section {
    margin-top: 20px;

    h4 {
      margin: 0 0 10px;
      color: #303133;
      font-size: 15px;
      font-weight: 500;
    }

    .description-text {
      margin: 0;
      color: #606266;
      line-height: 1.8;
      white-space: pre-line;
    }
  }

  .benefits-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;

    .benefit-tag {
      margin-right: 5px;
    }
  }

  .salary-text {
    color: #f56c6c;
    font-weight: 500;
    background: #fef0f0;
    padding: 2px 8px;
    border-radius: 4px;
  }
}

.batch-operations {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;

  .el-button-group {
    display: flex;
    gap: 8px;
  }

  .selected-count {
    color: #909399;
    font-size: 14px;
  }
}
</style>
