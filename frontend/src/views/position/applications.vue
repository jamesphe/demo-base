<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>职位申请管理</span>
      </div>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="申请状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable size="small">
            <el-option label="待处理" value="pending" />
            <el-option label="已审核" value="reviewed" />
            <el-option label="已安排面试" value="interview_scheduled" />
            <el-option label="已面试" value="interviewed" />
            <el-option label="已录用" value="offered" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已撤回" value="withdrawn" />
          </el-select>
        </el-form-item>
        <el-form-item label="职位名称">
          <el-input v-model="searchForm.jobTitle" placeholder="请输入职位名称" clearable size="small" />
        </el-form-item>
        <el-form-item label="候选人">
          <el-input v-model="searchForm.candidateName" placeholder="请输入候选人姓名" clearable size="small" />
        </el-form-item>
        <el-form-item label="学历要求">
          <el-select v-model="searchForm.education" placeholder="请选择学历" clearable size="small">
            <el-option label="大专" value="college" />
            <el-option label="本科" value="bachelor" />
            <el-option label="硕士" value="master" />
            <el-option label="博士" value="phd" />
          </el-select>
        </el-form-item>
        <el-form-item label="工作年限">
          <el-select v-model="searchForm.experience" placeholder="请选择工作年限" clearable size="small">
            <el-option label="应届生" value="fresh" />
            <el-option label="1年以下" value="0-1" />
            <el-option label="1-3年" value="1-3" />
            <el-option label="3-5年" value="3-5" />
            <el-option label="5-10年" value="5-10" />
            <el-option label="10年以上" value="10+" />
          </el-select>
        </el-form-item>
        <el-form-item label="匹配度">
          <el-select v-model="searchForm.matchScore" placeholder="请选择匹配度" clearable size="small">
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
            size="small"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="small" icon="el-icon-search" @click="handleSearch">查询</el-button>
          <el-button size="small" icon="el-icon-refresh" @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 批量操作和工具栏区域 -->
      <div class="toolbar-container">
        <!-- 批量操作工具栏 -->
        <div class="batch-operations">
          <div v-if="selectedApplications.length === 0" class="empty-selection-tip">
            <i class="el-icon-info"></i>
            <span>请在表格中勾选申请记录，以便进行批量操作</span>
          </div>
          <div class="operation-buttons">
            <el-tooltip content="请先选择申请记录" placement="top" :disabled="selectedApplications.length > 0">
              <el-button 
                size="small" 
                type="primary" 
                plain
                icon="el-icon-check"
                class="disabled-tip-btn"
                :disabled="selectedApplications.length === 0" 
                @click="handleBatchUpdateStatus('reviewed')"
              >批量标记为已审核</el-button>
            </el-tooltip>
            <el-tooltip content="请先选择申请记录" placement="top" :disabled="selectedApplications.length > 0">
              <el-button 
                size="small" 
                type="success" 
                plain
                icon="el-icon-chat-line-round"
                class="disabled-tip-btn"
                :disabled="selectedApplications.length === 0" 
                @click="handleBatchUpdateStatus('interviewed')"
              >批量标记为已面试</el-button>
            </el-tooltip>
            <el-tooltip content="请先选择申请记录" placement="top" :disabled="selectedApplications.length > 0">
              <el-button 
                size="small" 
                type="danger" 
                plain
                icon="el-icon-close"
                class="disabled-tip-btn"
                :disabled="selectedApplications.length === 0" 
                @click="handleBatchUpdateStatus('rejected')"
              >批量标记为已拒绝</el-button>
            </el-tooltip>
            <el-tooltip content="请先选择申请记录" placement="top" :disabled="selectedApplications.length > 0">
              <el-button 
                size="small" 
                type="warning" 
                plain
                icon="el-icon-date"
                class="disabled-tip-btn"
                :disabled="selectedApplications.length === 0" 
                @click="handleAddToInterview"
              >添加到面试</el-button>
            </el-tooltip>
          </div>
          <span class="selected-count" v-if="selectedApplications.length > 0">
            <i class="el-icon-tickets"></i>
            已选择 <b>{{ selectedApplications.length }}</b> 项
          </span>
        </div>
        
        <!-- 可以在这里添加其他操作按钮，如导出等 -->
        <div class="operation-container">
          <el-tooltip content="导出当前筛选条件下的申请数据" placement="top">
            <el-button 
              type="info" 
              plain
              size="small" 
              icon="el-icon-download"
            >导出数据</el-button>
          </el-tooltip>
        </div>
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
        :header-cell-style="{background:'#f6f8fa', color:'#303133', fontWeight: '500'}"
      >
        <el-table-column type="selection" width="55" align="center" fixed="left" />
        
        <!-- 候选人列 -->
        <el-table-column
          label="候选人"
          prop="candidate_name"
          align="center"
          min-width="120"
          class-name="candidate-column sortable-column"
          sortable="custom"
          fixed="left"
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
        
        <!-- 状态列 -->
        <el-table-column
          label="状态"
          prop="status"
          align="center"
          width="100"
          class-name="status-column sortable-column"
          sortable="custom"
          fixed="left"
        >
          <template slot-scope="scope">
            <el-tag
              :type="getStatusType(scope.row.status)"
              :class="['status-tag', `status-${scope.row.status}`]"
              effect="plain"
            >
              <i :class="getStatusIcon(scope.row.status)"></i>
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <!-- 职位名称列 -->
        <el-table-column
          label="职位名称"
          prop="job_title"
          align="center"
          min-width="180"
          class-name="job-column sortable-column"
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
        
        <!-- 匹配度列 -->
        <el-table-column
          label="匹配度"
          prop="match_score"
          align="center"
          width="120"
          class-name="match-column sortable-column"
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
        
        <!-- 工作年限列 -->
        <el-table-column
          label="工作年限"
          prop="experience_years"
          align="center"
          width="100"
          class-name="experience-column sortable-column"
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
          class-name="time-column sortable-column"
          sortable="custom"
        >
          <template slot-scope="scope">
            <span class="apply-time">{{ formatDateTime(scope.row.applyTime) }}</span>
          </template>
        </el-table-column>
        
        <!-- 简历名称列 -->
        <el-table-column
          label="简历名称"
          prop="resume_name"
          align="center"
          min-width="180"
          class-name="resume-column sortable-column"
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
        
        <!-- 部门列 -->
        <el-table-column
          label="部门"
          prop="department_name"
          align="center"
          min-width="120"
          class-name="department-column sortable-column"
          sortable="custom"
        >
          <template slot-scope="scope">
            <span>{{ scope.row.department_name || '-' }}</span>
          </template>
        </el-table-column>
        
        <!-- 发布人列 -->
        <el-table-column
          label="发布人"
          prop="publisher_name"
          align="center"
          min-width="120"
          class-name="publisher-column sortable-column"
          sortable="custom"
        >
          <template slot-scope="scope">
            <span>{{ scope.row.publisher_name || '-' }}</span>
          </template>
        </el-table-column>
        
        <!-- 租户列（仅超级管理员可见） -->
        <el-table-column
          v-if="isSuperuser"
          label="租户"
          prop="tenantName"
          align="center"
          min-width="120"
          class-name="tenant-column sortable-column"
          sortable="custom"
        >
          <template slot-scope="scope">
            <span>{{ scope.row.tenantName || '-' }}</span>
          </template>
        </el-table-column>
        
        <!-- 申请ID列 -->
        <el-table-column
          label="申请ID"
          prop="id"
          align="center"
          width="80"
          class-name="id-column sortable-column"
          sortable="custom"
        />
        
        <!-- 操作列 -->
        <el-table-column
          label="操作"
          align="center"
          width="280"
          fixed="right"
          class-name="action-column"
          header-align="center"
        >
          <template slot-scope="scope">
            <div class="action-buttons">
              <el-tooltip content="查看详情" placement="top">
                <el-button
                  size="mini"
                  type="primary"
                  plain
                  class="action-btn"
                  @click="handleView(scope.row)"
                >
                  <i class="el-icon-view" />
                </el-button>
              </el-tooltip>
              <el-tooltip content="更新状态" placement="top">
                <el-button
                  size="mini"
                  type="success"
                  plain
                  :disabled="scope.row.status === 'withdrawn'"
                  class="action-btn"
                  @click="handleUpdateStatus(scope.row)"
                >
                  <i class="el-icon-edit" />
                </el-button>
              </el-tooltip>
              <el-tooltip content="添加到面试" placement="top">
                <el-button
                  size="mini"
                  type="warning"
                  plain
                  class="action-btn"
                  @click="handleAddSingleToInterview(scope.row)"
                >
                  <i class="el-icon-date" />
                </el-button>
              </el-tooltip>
              <el-tooltip content="预览简历" placement="top">
                <el-button
                  size="mini"
                  type="info"
                  plain
                  class="action-btn"
                  @click="handlePreviewResume(scope.row)"
                >
                  <i class="el-icon-document" />
                </el-button>
              </el-tooltip>
              <el-dropdown trigger="click" @command="(command) => handleMoreActions(command, scope.row)">
                <el-button size="mini" type="primary" plain class="action-btn">
                  <i class="el-icon-more"></i>
                </el-button>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item command="download">下载简历</el-dropdown-item>
                  <el-dropdown-item command="send_email">发送邮件</el-dropdown-item>
                  <el-dropdown-item command="add_note">添加备注</el-dropdown-item>
                  <el-dropdown-item command="view_history" divided>查看处理记录</el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
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

    <!-- 添加面试对话框 -->
    <el-dialog title="添加到面试" :visible.sync="interviewDialogVisible" width="500px">
      <el-form :model="interviewForm" label-width="100px">
        <el-form-item label="面试类型">
          <el-select v-model="interviewForm.type" placeholder="请选择面试类型">
            <el-option label="初试" value="first" />
            <el-option label="复试" value="second" />
            <el-option label="终试" value="final" />
          </el-select>
        </el-form-item>
        <el-form-item label="面试时间">
          <el-date-picker
            v-model="interviewForm.time"
            type="datetime"
            placeholder="选择面试时间"
            value-format="yyyy-MM-dd HH:mm:ss"
            :picker-options="{
              disabledDate(time) {
                return time.getTime() < Date.now() - 8.64e7
              }
            }"
          />
        </el-form-item>
        <el-form-item label="面试时长">
          <el-input-number
            v-model="interviewForm.duration"
            :min="15"
            :max="240"
            :step="15"
            step-strictly
            placeholder="面试时长(分钟)"
          />
          <span style="margin-left: 5px">分钟</span>
        </el-form-item>
        <el-form-item label="面试官">
          <el-select
            v-model="interviewForm.interviewers"
            multiple
            filterable
            placeholder="请选择面试官"
            :loading="interviewerLoading"
          >
            <el-option
              v-for="item in formattedInterviewers"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="面试地点">
          <el-input v-model="interviewForm.location" placeholder="请输入面试地点" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input 
            type="textarea" 
            :rows="3" 
            placeholder="请输入备注信息" 
            v-model="interviewForm.notes"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="interviewDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="confirmAddToInterview" :loading="addingInterview">
          确 认
        </el-button>
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
import JobDetail, { showJobDetail } from '@/components/JobDetail'
import { batchUpdateStatus } from '@/api/job-application'
import { getInterviewerList as fetchInterviewers } from '@/api/interview'  // 临时导入API，用于调试

export default {
  name: 'PositionApplications',
  components: {
    Pagination,
    ResumeDetail,
    ResumePreview,
    JobDetail
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
      selectedApplications: [],
      interviewDialogVisible: false,
      interviewForm: {
        type: 'first',
        time: '',
        interviewers: [],
        location: '',
        notes: '',
        duration: 60
      },
      interviewerLoading: false,
      addingInterview: false
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
      'currentPosition'
    ]),
    ...mapGetters('interview', [
      'interviewerList'
    ]),
    ...mapGetters([
      'isSuperuser'
    ]),
    baseApiUrl() {
      return process.env.VUE_APP_BASE_API || ''
    },
    authToken() {
      return getToken()
    },
    formatResumeDetail() {
      return this.currentDetail || {}
    },
    formattedInterviewers() {
      if (!this.interviewerList || !Array.isArray(this.interviewerList)) {
        return []
      }
      
      const formatted = this.interviewerList.map(item => ({
        id: item.id,
        name: item.username || item.name || '未知'
      }))
      return formatted
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
    ...mapActions('interview', [
      'getInterviewerList',
      'createInterview'
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

        const result = await this.getApplicationList(params)
      } catch (error) {
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
        interview_scheduled: 'warning',
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
        interview_scheduled: '已安排面试',
        interviewed: '已面试',
        offered: '已录用',
        rejected: '已拒绝',
        withdrawn: '已撤回'
      }
      return statusMap[status]
    },
    getStatusIcon(status) {
      const iconMap = {
        pending: 'el-icon-time',
        reviewed: 'el-icon-view',
        interview_scheduled: 'el-icon-date',
        interviewed: 'el-icon-chat-line-round',
        offered: 'el-icon-check',
        rejected: 'el-icon-close',
        withdrawn: 'el-icon-back'
      }
      return iconMap[status] || 'el-icon-info'
    },
    getMatchScoreColor(score) {
      if (score >= 80) return '#67C23A'
      if (score >= 60) return '#E6A23C'
      return '#F56C6C'
    },
    async handleView(row) {
      this.resumeDetailVisible = true
      this.resumeDetailLoading = true
      try {
        await this.getResumeDetail(row.resumeId)
      } catch (error) {
        this.$message.error('获取简历详情失败')
      } finally {
        this.resumeDetailLoading = false
      }
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
        return '格式化错误'
      }
    },
    handleSelectionChange(selection) {
      this.selectedApplications = selection;
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
    handleSortChange(column) {
      if (column.prop && column.order) {
        this.listQuery.sortField = column.prop
        this.listQuery.sortOrder = column.order === 'ascending' ? 'asc' : 'desc'
      } else {
        this.listQuery.sortField = ''
        this.listQuery.sortOrder = ''
      }
      this.getList()
    },
    handleViewJob(job) {
      showJobDetail(job)
    },
    handleAddToInterview() {
      if (this.selectedApplications.length === 0) {
        this.$message.warning('请先选择申请记录')
        return
      }
      
      this.interviewDialogVisible = true
      this.interviewForm = {
        type: 'first',
        time: '',
        interviewers: [],
        location: '',
        notes: '',
        duration: 60
      }
      this.fetchInterviewers()
    },
    handleMoreActions(command, row) {
      // Implementation of more actions
    },
    handlePreviewResume(row) {
      // Implementation of preview resume
    },
    handleResumeDialogClose() {
      // Implementation of resume dialog close
    },
    handlePreviewClose() {
      // Implementation of preview close
    },
    handleAddSingleToInterview(row) {
      this.interviewDialogVisible = true
      this.interviewForm = {
        type: 'first',
        time: '',
        interviewers: [],
        location: '',
        notes: '',
        duration: 60
      }
      this.selectedApplications = [row]
      this.fetchInterviewers()
    },
    
    async fetchInterviewers() {
      try {
        this.interviewerLoading = true
        
        // 获取面试官列表 - 通过Vuex
        const data = await this.getInterviewerList()
        
        // 如果store中数据无效，尝试手动更新
        if (!this.interviewerList || !Array.isArray(this.interviewerList) || this.interviewerList.length === 0) {
          if (data && Array.isArray(data)) {
            this.$store.commit('interview/SET_INTERVIEWER_LIST', data)
          } else {
            // 如果action返回的数据也有问题，直接调用API
            const response = await fetchInterviewers()
            
            if (response && response.data && Array.isArray(response.data)) {
              this.$store.commit('interview/SET_INTERVIEWER_LIST', response.data)
            } else {
              this.$message.error('API返回的面试官数据格式不正确')
            }
          }
        }
      } catch (error) {
        this.$message.error('获取面试官列表失败')
      } finally {
        this.interviewerLoading = false
      }
    },
    handleBatchUpdateStatus(status) {
      if (this.selectedApplications.length === 0) {
        this.$message.warning('请先选择申请记录')
        return
      }
      
      const statusTextMap = {
        reviewed: '已审核',
        interviewed: '已面试',
        rejected: '已拒绝'
      }
      
      this.$confirm(`确定要将所选 ${this.selectedApplications.length} 条申请记录标记为"${statusTextMap[status]}"吗？`, '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const applicationIds = this.selectedApplications.map(app => app.id)
          
          await batchUpdateStatus({
            applications: applicationIds.map(id => ({ id })),
            status: status,
            notes: `批量更新状态为：${statusTextMap[status]}`
          })
          
          this.$message.success(`已成功将 ${this.selectedApplications.length} 条申请记录标记为"${statusTextMap[status]}"`)
          this.getList()
        } catch (error) {
          this.$message.error('批量更新状态失败')
        }
      }).catch(() => {
        // 用户取消操作
      })
    },
    async confirmAddToInterview() {
      if (!this.interviewForm.time) {
        this.$message.warning('请选择面试时间')
        return
      }
      
      if (this.interviewForm.interviewers.length === 0) {
        this.$message.warning('请选择至少一名面试官')
        return
      }
      
      try {
        this.addingInterview = true
        
        // 1. 准备候选人数据
        const applicationIds = this.selectedApplications.map(app => app.id)
        const candidates = this.selectedApplications.map(app => ({
          applicationId: app.id,
          resumeId: app.resumeId,
          candidate_name: app.candidateName,
          candidate_phone: app.candidatePhone || '',
          candidate_email: app.candidateEmail || ''
        }))
        
        // 2. 准备面试数据
        const interviewData = {
          type: this.interviewForm.type,
          time: this.interviewForm.time,
          location: this.interviewForm.location,
          interviewer_id: this.interviewForm.interviewers[0], // 使用第一个面试官ID
          interviewers: this.interviewForm.interviewers,
          notes: this.interviewForm.notes,
          candidates: candidates,
          job_id: this.selectedApplications[0].job?.id || null, // 调整为job_id
          resume_id: candidates[0].resumeId, // 直接传递resumeId
          duration: this.interviewForm.duration
        }
        
        // 3. 创建面试记录
        const result = await this.createInterview(interviewData)
        
        this.$message.success('面试安排已添加')
        this.interviewDialogVisible = false
        
        // 4. 刷新申请列表
        this.getList()
      } catch (error) {
        // 处理面试时间冲突错误
        if (error.response && error.response.data && error.response.data.detail) {
          const detail = error.response.data.detail
          if (typeof detail === 'object' && detail.message === '面试时间冲突') {
            this.$message.error(detail.details || '面试官在该时间段已有其他面试安排，请选择其他时间')
          } else {
            this.$message.error(detail)
          }
        } else {
          this.$message.error('添加面试失败')
        }
      } finally {
        this.addingInterview = false
      }
    },
    getInterviewTypeText(type) {
      const typeMap = {
        first: '初试',
        second: '复试',
        final: '终试'
      }
      return typeMap[type] || '面试'
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.search-form {
  padding: 18px 0;
  margin-bottom: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  padding-left: 15px;
  
  .el-form-item {
    margin-bottom: 18px;
    margin-right: 18px;
  }
}

.toolbar-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.operation-container {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 12px 15px;
  
  .filter-item {
    padding: 8px 15px;
  }
  
  ::v-deep .el-button--info.is-plain {
    border-color: #909399;
    color: #909399;
    background-color: rgba(144, 147, 153, 0.1);
  }
  
  ::v-deep .el-button.is-plain:hover {
    background-color: #fff;
  }
}

.batch-operations {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 12px 15px;
  flex-wrap: wrap;
  
  .empty-selection-tip {
    display: flex;
    align-items: center;
    color: #606266;
    font-size: 14px;
    background-color: #ffffff;
    padding: 8px 15px;
    border-radius: 4px;
    margin-right: 15px;
    margin-bottom: 10px;
    border: 1px dashed #DCDFE6;
    
    i {
      margin-right: 8px;
      color: #E6A23C;
      font-size: 16px;
    }
  }
  
  .operation-buttons {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-right: 15px;
    
    .disabled-tip-btn.el-button.is-disabled {
      position: relative;
      border-width: 1px;
      border-style: dashed;
      font-weight: 500;
      
      &::before {
        content: "!";
        position: absolute;
        top: -8px;
        right: -4px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background-color: #909399;
        color: #fff;
        font-size: 12px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s;
      }
      
      &:hover::before {
        transform: scale(1.2);
      }
    }
    
    .disabled-tip-btn.el-button--primary.is-disabled::before {
      background-color: #409EFF;
    }
    
    .disabled-tip-btn.el-button--success.is-disabled::before {
      background-color: #67C23A;
    }
    
    .disabled-tip-btn.el-button--danger.is-disabled::before {
      background-color: #F56C6C;
    }
    
    .disabled-tip-btn.el-button--warning.is-disabled::before {
      background-color: #E6A23C;
    }
    
    ::v-deep .el-button--primary.is-plain {
      border-color: #409EFF;
      color: #409EFF;
      background-color: rgba(64, 158, 255, 0.1);
    }
    
    ::v-deep .el-button--success.is-plain {
      border-color: #67C23A;
      color: #67C23A;
      background-color: rgba(103, 194, 58, 0.1);
    }
    
    ::v-deep .el-button--danger.is-plain {
      border-color: #F56C6C;
      color: #F56C6C;
      background-color: rgba(245, 108, 108, 0.1);
    }
    
    ::v-deep .el-button--warning.is-plain {
      border-color: #E6A23C;
      color: #E6A23C;
      background-color: rgba(230, 162, 60, 0.1);
    }
    
    ::v-deep .el-button.is-plain:hover {
      background-color: #fff;
    }
    
    ::v-deep .el-button.is-disabled, 
    ::v-deep .el-button.is-disabled:hover {
      color: #303133;
      cursor: not-allowed;
      background-color: #F7F9FC;
      border-color: #DCDFE6;
      border-style: dashed;
      border-width: 1px;
      opacity: 0.9;
    }
    
    ::v-deep .el-button--primary.is-plain.is-disabled, 
    ::v-deep .el-button--primary.is-plain.is-disabled:hover {
      color: #306199;
      background-color: #ECF5FF;
      border-color: #B3D8FF;
    }
    
    ::v-deep .el-button--success.is-plain.is-disabled, 
    ::v-deep .el-button--success.is-plain.is-disabled:hover {
      color: #48803F;
      background-color: #F0F9EB;
      border-color: #C2E7B0;
    }
    
    ::v-deep .el-button--warning.is-plain.is-disabled, 
    ::v-deep .el-button--warning.is-plain.is-disabled:hover {
      color: #A67832;
      background-color: #FDF6EC;
      border-color: #F5DAB1;
    }
    
    ::v-deep .el-button--danger.is-plain.is-disabled, 
    ::v-deep .el-button--danger.is-plain.is-disabled:hover {
      color: #A13E3E;
      background-color: #FEF0F0;
      border-color: #F9C0C0;
    }
    
    ::v-deep .el-button--info.is-plain.is-disabled, 
    ::v-deep .el-button--info.is-plain.is-disabled:hover {
      color: #5A5B5E;
      background-color: #F4F4F5;
      border-color: #D3D4D6;
    }
  }
  
  .selected-count {
    color: #606266;
    font-size: 14px;
    background-color: #ffffff;
    padding: 6px 12px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    border: 1px solid #e4e7ed;
    
    i {
      margin-right: 5px;
      color: #409EFF;
    }
    
    b {
      color: #409EFF;
      margin: 0 3px;
    }
  }
}

.application-table {
  margin-bottom: 20px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #ebeef5;
  
  ::v-deep .el-table__header-wrapper {
    position: relative;
    
    &::after {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 3px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
      z-index: 1;
    }
    
    th {
      height: 50px;
      padding: 4px 0;
      position: relative;
      background-color: #f6f8fa !important;
      transition: background-color 0.2s;
      border-right: 1px solid #ebeef5;
      
      &:hover {
        background-color: #f0f2f5 !important;
      }
      
      .cell {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
        display: flex;
        align-items: center;
        justify-content: center;
        
        .el-icon-arrow-down {
          color: #909399;
          font-size: 12px;
          margin-left: 5px;
          transition: transform 0.2s;
          
          &:hover {
            color: #409EFF;
            transform: rotate(180deg);
          }
        }
      }
      
      .caret-wrapper {
        height: 30px;
        margin-left: 5px;
      }
      
      // 更新排序箭头的通用样式，使所有可排序列都清晰可见
      .sortable-column, th.sortable-column {
        .caret-wrapper {
          margin-left: 5px;
          display: inline-flex;
          flex-direction: column;
          align-items: center;
          height: 34px;
          width: 24px;
          vertical-align: middle;
          cursor: pointer;
          overflow: initial;
          position: relative;
          
          .sort-caret {
            width: 0;
            height: 0;
            border: 5px solid transparent;
            position: absolute;
            left: 7px;
            
            &.ascending {
              border-bottom-color: #C0C4CC;
              top: 5px;
            }
            
            &.descending {
              border-top-color: #C0C4CC;
              bottom: 7px;
            }
          }
        }
        
        &.ascending .sort-caret.ascending {
          border-bottom-color: #409EFF;
        }
        
        &.descending .sort-caret.descending {
          border-top-color: #409EFF;
        }
      }
      
      &.ascending .sort-caret.ascending {
        border-bottom-color: #409EFF;
      }
      
      &.descending .sort-caret.descending {
        border-top-color: #409EFF;
      }
      
      &.ascending, &.descending {
        background-color: #ecf5ff !important;
        
        .cell {
          color: #409EFF;
        }
      }
      
      &.is-leaf {
        border-bottom: 2px solid #ebeef5;
      }
    }
  }
  
  // 为所有可排序列应用相同的排序箭头样式
  ::v-deep th.sortable-column .caret-wrapper {
    position: relative;
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    height: 34px;
    width: 24px;
    vertical-align: middle;
    cursor: pointer;
    overflow: initial;
    
    .sort-caret {
      width: 0;
      height: 0;
      border: 5px solid transparent;
      position: absolute;
      left: 7px;
      
      &.ascending {
        border-bottom-color: #606266;
        top: 5px;
      }
      
      &.descending {
        border-top-color: #606266;
        bottom: 7px;
      }
    }
  }
  
  // 高亮当前排序列的箭头
  ::v-deep th.ascending .sort-caret.ascending {
    border-bottom-color: #409EFF !important;
  }
  
  ::v-deep th.descending .sort-caret.descending {
    border-top-color: #409EFF !important;
  }
  
  ::v-deep .el-table__body-wrapper {
    .el-table__row {
      &:hover > td {
        background-color: #f5f7fa;
      }
      
      td {
        transition: background-color 0.2s;
        border-bottom: 1px solid #ebeef5;
      }
      
      &:last-child td {
        border-bottom: none;
      }
    }
  }
  
  ::v-deep .el-table--border::after, 
  ::v-deep .el-table--group::after, 
  ::v-deep .el-table::before {
    background-color: #ebeef5;
  }
  
  // 表格行的斑马纹和悬浮效果
  ::v-deep .el-table--striped .el-table__body tr.el-table__row--striped td {
    background-color: #fafafa;
  }
  
  ::v-deep .el-table__body tr.hover-row > td {
    background-color: #f5f7fa !important;
  }
  
  ::v-deep .el-table__row {
    height: 55px;
  }
  
  .job-title,
  .candidate-name,
  .resume-name {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
  }
  
  .candidate-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .el-tag {
      margin-top: 5px;
    }
  }
  
  .match-score-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    
    .match-progress {
      width: 80%;
    }
    
    .match-reason-btn {
      margin-left: 5px;
    }
  }
  
  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 8px;
    
    .action-btn {
      padding: 5px 8px;
      margin: 0 2px;
      
      i {
        margin-right: 0;
        font-size: 14px;
      }
      
      &:hover {
        transform: translateY(-1px);
        transition: all 0.2s;
      }
    }
    
    .el-dropdown {
      margin-left: 2px;
      
      .el-button {
        padding: 5px 8px;
      }
    }
  }
  
  .apply-time, 
  .experience-years {
    color: #606266;
    font-size: 13px;
  }
  
  .status-tag {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0 10px;
    min-width: 80px;
    height: 28px;
    font-weight: 500;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s;
    border-radius: 4px;
    
    i {
      margin-right: 5px;
      font-size: 14px;
    }
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
  }
  
  .status-pending {
    background-color: #e9f1ff !important;
    color: #3b73b2 !important;
    border-color: #a6c5ff !important;
  }
  
  .status-reviewed {
    background-color: #fdf6ec !important;
    color: #a6710c !important;
    border-color: #f0cea0 !important;
  }
  
  .status-interview_scheduled {
    background-color: #f0f9eb !important;
    color: #6d9e38 !important;
    border-color: #c2e7b0 !important;
  }
  
  .status-interviewed {
    background-color: #f0f9eb !important;
    color: #6d9e38 !important;
    border-color: #c2e7b0 !important;
  }
  
  .status-offered {
    background-color: #e1f5ec !important;
    color: #1c9264 !important;
    border-color: #a8e0c9 !important;
  }
  
  .status-rejected {
    background-color: #fee6e6 !important;
    color: #c03d3d !important;
    border-color: #f9c0c0 !important;
  }
  
  .status-withdrawn {
    background-color: #f4f4f5 !important;
    color: #5f5f60 !important;
    border-color: #dcdee0 !important;
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

::v-deep .el-tooltip__popper {
  font-size: 12px;
  padding: 6px 10px;
}

::v-deep .el-dropdown-menu {
  padding: 5px 0;
  
  .el-dropdown-menu__item {
    line-height: 32px;
    padding: 0 15px;
    font-size: 13px;
    
    i {
      margin-right: 8px;
    }
    
    &.divided {
      border-top: 1px solid #ebeef5;
      margin-top: 5px;
      padding-top: 5px;
    }
  }
}
</style>