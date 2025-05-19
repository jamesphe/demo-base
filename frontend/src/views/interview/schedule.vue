<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>面试安排</span>
        <el-button
          style="float: right; padding: 3px 0"
          type="text"
          @click="handleAddInterview"
        >新增面试</el-button>
      </div>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="面试类型">
          <el-select v-model="searchForm.type" placeholder="请选择类型" clearable size="small">
            <el-option label="初试" value="first" />
            <el-option label="复试" value="second" />
            <el-option label="终试" value="final" />
          </el-select>
        </el-form-item>
        <el-form-item label="面试状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable size="small">
            <el-option label="待面试" value="scheduled" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="面试时间">
          <el-date-picker
            v-model="searchForm.timeRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
            clearable
            size="small"
          />
        </el-form-item>
        <el-form-item label="候选人">
          <el-input v-model="searchForm.candidateName" placeholder="请输入候选人姓名" clearable size="small" />
        </el-form-item>
        <el-form-item label="面试官">
          <el-select
            v-model="searchForm.interviewerId"
            placeholder="请选择面试官"
            clearable
            size="small"
          >
            <el-option
              v-for="item in interviewerOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="small" icon="el-icon-search" @click="handleSearch">查询</el-button>
          <el-button size="small" icon="el-icon-refresh" @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 面试列表 -->
      <el-table
        v-loading="loading"
        :data="interviewList"
        element-loading-text="加载中..."
        border
        fit
        highlight-current-row
        class="interview-table"
      >
        <el-table-column type="selection" width="55" align="center" />
        
        <!-- 面试ID -->
        <el-table-column
          label="面试ID"
          prop="id"
          align="center"
          width="80"
          sortable="custom"
        />

        <!-- 候选人 -->
        <el-table-column
          label="候选人"
          prop="resumeTitle"
          align="center"
          min-width="120"
        >
          <template slot-scope="scope">
            <div class="candidate-info">
              <span class="candidate-name clickable" @click="handleCandidateClick(scope.row)">{{ (scope.row.resume && scope.row.resume.name) || scope.row.resumeTitle || '-' }}</span>
              <el-tag size="mini" type="info">{{ scope.row.jobTitle || '-' }}</el-tag>
            </div>
          </template>
        </el-table-column>

        <!-- 面试类型 -->
        <el-table-column
          label="面试类型"
          prop="interviewType"
          align="center"
          width="100"
        >
          <template slot-scope="scope">
            <el-tag :type="getInterviewTypeTag(scope.row.interviewType)">
              {{ getInterviewTypeText(scope.row.interviewType) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 面试时间 -->
        <el-table-column
          label="面试时间"
          prop="scheduleTime"
          align="center"
          width="160"
          sortable="custom"
        >
          <template slot-scope="scope">
            <span>{{ formatDateTime(scope.row.scheduleTime) }}</span>
          </template>
        </el-table-column>

        <!-- 面试地点 -->
        <el-table-column
          label="面试地点"
          prop="location"
          align="center"
          min-width="120"
        />

        <!-- 面试官 -->
        <el-table-column
          label="面试官"
          prop="interviewerName"
          align="center"
          min-width="120"
        >
          <template slot-scope="scope">
            <div v-if="scope.row.interviewers && scope.row.interviewers.length > 0">
              <el-tag
                v-for="interviewer in scope.row.interviewers"
                :key="interviewer.id"
                size="mini"
                class="interviewer-tag"
                style="margin-right: 5px; margin-bottom: 5px;"
              >
                {{ interviewer.username }}
              </el-tag>
            </div>
            <div v-else-if="scope.row.interviewer_names && scope.row.interviewer_names.length > 0">
              <el-tag
                v-for="(name, index) in scope.row.interviewer_names"
                :key="index"
                size="mini"
                class="interviewer-tag"
                style="margin-right: 5px; margin-bottom: 5px;"
              >
                {{ name }}
              </el-tag>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <!-- 状态 -->
        <el-table-column
          label="状态"
          prop="status"
          align="center"
          width="100"
        >
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 操作 -->
        <el-table-column
          label="操作"
          align="center"
          width="320"
          fixed="right"
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
              <el-tooltip content="面试准备" placement="top">
                <el-button
                  size="mini"
                  type="success"
                  plain
                  class="action-btn"
                  @click="handlePreparation(scope.row)"
                >
                  <i class="el-icon-notebook-2" />
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑面试" placement="top">
                <el-button
                  size="mini"
                  type="success"
                  plain
                  :disabled="scope.row.status !== 'scheduled'"
                  @click="handleEdit(scope.row)"
                >编辑</el-button>
              </el-tooltip>
              <el-tooltip content="取消面试" placement="top">
                <el-button
                  size="mini"
                  type="danger"
                  plain
                  :disabled="scope.row.status !== 'scheduled'"
                  @click="handleCancel(scope.row)"
                >取消</el-button>
              </el-tooltip>
              <el-tooltip content="评估面试" placement="top">
                <el-button
                  size="mini"
                  type="warning"
                  plain
                  :disabled="scope.row.status !== 'completed'"
                  @click="handleEvaluate(scope.row)"
                >评估</el-button>
              </el-tooltip>
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

    <!-- 新增/编辑面试对话框 -->
    <el-dialog
      :title="dialogType === 'add' ? '新增面试' : '编辑面试'"
      :visible.sync="dialogVisible"
      width="500px"
    >
      <el-form
        ref="interviewForm"
        :model="interviewForm"
        :rules="interviewRules"
        label-width="100px"
      >
        <el-form-item label="面试类型" prop="type">
          <el-select v-model="interviewForm.type" placeholder="请选择面试类型">
            <el-option label="初试" value="first" />
            <el-option label="复试" value="second" />
            <el-option label="终试" value="final" />
          </el-select>
        </el-form-item>
        <el-form-item label="面试时间" prop="time">
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
        <el-form-item label="面试官" prop="interviewers">
          <el-select
            v-model="interviewForm.interviewers"
            multiple
            filterable
            placeholder="请选择面试官"
          >
            <el-option
              v-for="item in interviewerOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="面试地点" prop="location">
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
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitInterviewForm" :loading="submitting">
          确 定
        </el-button>
      </div>
    </el-dialog>

    <!-- 面试详情对话框 -->
    <el-dialog
      title="面试详情"
      :visible.sync="detailDialogVisible"
      width="650px"
      custom-class="interview-detail-dialog"
    >
      <div v-loading="currentInterviewLoading" class="interview-detail">
        <div class="interview-header">
          <div class="interview-tag">
            <el-tag :type="getInterviewTypeTag(currentInterview.interviewType)" size="medium" effect="plain">
              {{ getInterviewTypeText(currentInterview.interviewType) }}
            </el-tag>
            <el-tag :type="getStatusType(currentInterview.status)" class="status-tag" size="medium" effect="plain">
              {{ getStatusText(currentInterview.status) }}
            </el-tag>
          </div>
          <div class="interview-id"># {{ currentInterview.id }}</div>
        </div>

        <div class="candidate-box">
          <div class="info-title">
            <i class="el-icon-user"></i> 候选人信息
          </div>
          <div class="info-content">
            <span class="candidate-name">{{ (currentInterview.resume && currentInterview.resume.name) || currentInterview.resumeTitle || '-' }}</span>
            <span class="job-title">{{ currentInterview.jobTitle || '' }}</span>
          </div>
        </div>

        <div class="info-row">
          <div class="info-col">
            <div class="info-title">
              <i class="el-icon-date"></i> 面试时间
            </div>
            <div class="info-content time-block">
              {{ formatDateTime(currentInterview.scheduleTime) }}
            </div>
          </div>
          <div class="info-col">
            <div class="info-title">
              <i class="el-icon-location"></i> 面试地点
            </div>
            <div class="info-content">
              {{ currentInterview.location || '-' }}
            </div>
          </div>
        </div>

        <div class="interviewer-box">
          <div class="info-title">
            <i class="el-icon-user-solid"></i> 面试官
          </div>
          <div class="info-content">
            <div v-if="currentInterview.interviewers && currentInterview.interviewers.length > 0">
              <el-tag
                v-for="interviewer in currentInterview.interviewers"
                :key="interviewer.id"
                size="small"
                effect="plain"
                class="interviewer-tag"
              >
                <i class="el-icon-user"></i> {{ interviewer.username }}
              </el-tag>
            </div>
            <span v-else class="empty-text">暂无面试官</span>
          </div>
        </div>

        <div class="notes-box">
          <div class="info-title">
            <i class="el-icon-document"></i> 备注信息
          </div>
          <div class="info-content">
            <div class="notes-content">{{ currentInterview.notes || '暂无备注信息' }}</div>
          </div>
        </div>
        
        <div class="detail-actions">
          <el-button type="primary" size="small" round @click="handlePreparation(currentInterview)">
            <i class="el-icon-notebook-2"></i> 面试准备
          </el-button>
          <el-button 
            type="success" 
            size="small" 
            round
            :disabled="currentInterview.status !== 'scheduled'"
            @click="handleEdit(currentInterview)"
          >
            <i class="el-icon-edit"></i> 编辑面试
          </el-button>
          <el-button 
            type="warning" 
            size="small" 
            round
            :disabled="currentInterview.status !== 'completed'"
            @click="handleEvaluate(currentInterview)"
          >
            <i class="el-icon-star-on"></i> 评估面试
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 候选人详情对话框 -->
    <el-dialog
      title="候选人详情"
      :visible.sync="candidateDetailVisible"
      width="800px"
      custom-class="candidate-detail-dialog"
    >
      <div v-loading="detailLoading" class="candidate-detail-container">
        <resume-detail :detail="currentDetail" :loading="detailLoading" />
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import Pagination from '@/components/Pagination'
import ResumeDetail from '@/components/ResumeDetail'
import { formatDateTime } from '@/utils/format'

export default {
  name: 'InterviewSchedule',
  components: {
    Pagination,
    ResumeDetail
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
        type: '',
        status: '',
        timeRange: [],
        candidateName: '',
        interviewerId: ''
      },
      dialogVisible: false,
      dialogType: 'add', // 'add' 或 'edit'
      interviewForm: {
        type: 'first',
        time: '',
        interviewers: [],
        location: '',
        notes: '',
        resumeId: '',
        jobId: ''
      },
      interviewRules: {
        type: [
          { required: true, message: '请选择面试类型', trigger: 'change' }
        ],
        time: [
          { required: true, message: '请选择面试时间', trigger: 'change' }
        ],
        interviewers: [
          { required: true, message: '请选择至少一名面试官', trigger: 'change' }
        ],
        location: [
          { required: true, message: '请输入面试地点', trigger: 'blur' }
        ]
      },
      submitting: false,
      currentInterviewId: null,
      detailDialogVisible: false,
      currentInterviewLoading: false,
      currentInterview: {},
      // 候选人详情对话框
      candidateDetailVisible: false
    }
  },
  computed: {
    ...mapGetters('interview', [
      'interviewList',
      'total',
      'loading',
      'interviewerList'
    ]),
    ...mapGetters('resume', [
      'currentDetail',
      'detailLoading'
    ]),
    interviewerOptions() {
      console.log('面试官列表数据:', this.interviewerList)
      return this.interviewerList.map(item => ({
        id: item.id,
        name: item.username
      }))
    }
  },
  created() {
    console.log('组件创建时的状态:', {
      interviewList: this.interviewList,
      total: this.total,
      loading: this.loading
    })
    this.getList()
    this.getInterviewerList()
  },
  methods: {
    ...mapActions('interview', [
      'getInterviewList',
      'createInterviews',
      'updateInterview',
      'deleteInterview',
      'getInterviewerList'
    ]),
    ...mapActions('resume', [
      'getResumeDetail'
    ]),
    async getList() {
      try {
        const params = {
          ...this.listQuery,
          ...this.searchForm,
          timeStart: this.searchForm.timeRange?.[0],
          timeEnd: this.searchForm.timeRange?.[1]
        }
        console.log('获取面试列表参数:', params)
        await this.getInterviewList(params)
        console.log('获取面试列表后的状态:', {
          interviewList: this.interviewList,
          total: this.total,
          loading: this.loading
        })
      } catch (error) {
        console.error('获取面试列表失败:', error)
        this.$message.error('获取面试列表失败')
      }
    },
    handleSearch() {
      this.listQuery.page = 1
      this.getList()
    },
    resetSearch() {
      this.searchForm = {
        type: '',
        status: '',
        timeRange: [],
        candidateName: '',
        interviewerId: ''
      }
      this.listQuery.page = 1
      this.getList()
    },
    handleAddInterview() {
      this.dialogType = 'add'
      this.interviewForm = {
        type: 'first',
        time: '',
        interviewers: [],
        location: '',
        notes: '',
        resumeId: '',
        jobId: ''
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogType = 'edit'
      this.currentInterviewId = row.id
      
      // 设置表单数据
      this.interviewForm = {
        type: row.interviewType,
        time: row.scheduleTime,
        // 设置面试官列表
        interviewers: row.interviewers ? row.interviewers.map(item => item.id) : [],
        location: row.location,
        notes: row.notes,
        resumeId: row.resume_id,
        jobId: row.job_id
      }
      
      this.dialogVisible = true
    },
    async handleCancel(row) {
      try {
        await this.$confirm('确认取消该面试吗？', '提示', {
          type: 'warning'
        })
        await this.updateInterview({
          id: row.id,
          data: { status: 'cancelled' }
        })
        this.$message.success('面试已取消')
        this.getList()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('取消面试失败:', error)
          this.$message.error('取消面试失败')
        }
      }
    },
    handleView(row) {
      this.currentInterview = row
      this.detailDialogVisible = true
      this.currentInterviewLoading = false
    },
    handlePreparation(row) {
      this.$router.push(`/interview/preparation/${row.id}`)
    },
    handleEvaluate(row) {
      this.$router.push(`/interview/evaluation/${row.id}`)
    },
    async submitInterviewForm() {
      try {
        await this.$refs.interviewForm.validate()
        
        this.submitting = true
        
        if (this.dialogType === 'add') {
          await this.createInterviews(this.interviewForm)
          this.$message.success('面试创建成功')
        } else {
          await this.updateInterview({
            id: this.currentInterviewId,
            data: this.interviewForm
          })
          this.$message.success('面试更新成功')
        }
        
        this.dialogVisible = false
        this.resetForm()
        this.getList()
      } catch (error) {
        console.error('提交表单失败:', error)
        if (error.response && error.response.data && error.response.data.detail) {
          const detail = error.response.data.detail
          if (typeof detail === 'object' && detail.message === '面试时间冲突') {
            this.$message.error(detail.details || '面试官在该时间段已有其他面试安排，请选择其他时间')
          } else {
            this.$message.error(detail)
          }
        } else {
          this.$message.error('提交表单失败')
        }
      } finally {
        this.submitting = false
      }
    },
    getInterviewTypeText(type) {
      const typeMap = {
        first: '初试',
        second: '复试',
        final: '终试'
      }
      return typeMap[type] || '面试'
    },
    getInterviewTypeTag(type) {
      const tagMap = {
        first: 'primary',
        second: 'success',
        final: 'warning'
      }
      return tagMap[type] || 'info'
    },
    getStatusText(status) {
      const statusMap = {
        scheduled: '待面试',
        completed: '已完成',
        cancelled: '已取消'
      }
      return statusMap[status] || '未知'
    },
    getStatusType(status) {
      const typeMap = {
        scheduled: 'warning',
        completed: 'success',
        cancelled: 'info'
      }
      return typeMap[status] || ''
    },
    formatDateTime(timestamp) {
      if (!timestamp) return '-'
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    resetForm() {
      this.interviewForm = {
        type: 'first',
        time: '',
        interviewers: [],
        location: '',
        notes: '',
        resumeId: '',
        jobId: ''
      }
    },
    async handleCandidateClick(row) {
      // 添加调试信息，查看面试记录的完整数据
      console.log('面试记录数据:', row)
      console.log('简历ID:', row.resume_id)
      console.log('候选人信息:', row.resume)
      
      // 尝试获取简历ID，优先使用resume_id，然后尝试其他可能的字段
      const resumeId = row.resume_id || row.resumeId || (row.resume && row.resume.id);
      
      if (!resumeId) {
        // 检查有没有其他可能的ID字段
        console.log('寻找替代ID:',
          '候选人ID:', row.candidate_id,
          '简历名称:', row.resumeTitle
        )
        
        this.$message.warning('该面试无关联简历信息')
        return
      }
      
      console.log('将使用简历ID获取详情:', resumeId)
      this.candidateDetailVisible = true
      
      try {
        // 通过store获取简历详情
        await this.getResumeDetail(resumeId)
      } catch (error) {
        console.error('获取候选人简历详情失败:', error)
        this.$message.error('获取候选人简历详情失败')
      }
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

.interview-table {
  margin-bottom: 20px;
  
  .candidate-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .candidate-name {
      margin-bottom: 5px;
      font-weight: 500;
      
      &.clickable {
        color: #409EFF;
        cursor: pointer;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
  
  .interviewer-tag {
    margin: 2px;
  }
  
  .action-buttons {
    display: flex;
    flex-wrap: nowrap;
    justify-content: center;
    gap: 5px;
    
    .action-btn {
      margin: 0;
    }
  }
}

::v-deep .el-dialog {
  border-radius: 8px;
  
  .el-dialog__header {
    padding: 20px;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .el-dialog__body {
    padding: 30px 20px;
  }
  
  .el-dialog__footer {
    padding: 20px;
    border-top: 1px solid #e4e7ed;
  }
}

.interview-detail {
  padding: 10px;
}

.interview-detail-dialog {
  .interview-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px dashed #ebeef5;

    .interview-tag {
      display: flex;
      align-items: center;

      .el-tag {
        margin-right: 10px;
        padding: 0 12px;
        height: 28px;
        line-height: 26px;
      }
    }

    .interview-id {
      font-size: 14px;
      color: #909399;
      font-weight: 500;
      background: #f5f7fa;
      padding: 4px 10px;
      border-radius: 12px;
    }
  }

  .candidate-box {
    background: #f9fafc;
    border-radius: 6px;
    padding: 15px;
    margin-bottom: 20px;

    .info-title {
      font-weight: 500;
      margin-bottom: 10px;
      font-size: 15px;
      color: #303133;

      i {
        margin-right: 5px;
        color: #409EFF;
      }
    }

    .info-content {
      display: flex;
      align-items: center;

      .candidate-name {
        font-size: 16px;
        font-weight: 600;
        margin-right: 10px;
      }

      .job-title {
        font-size: 13px;
        color: #909399;
        background: #f0f2f5;
        padding: 2px 8px;
        border-radius: 4px;
      }
    }
  }

  .info-row {
    display: flex;
    margin-bottom: 20px;
    gap: 20px;

    .info-col {
      flex: 1;
      background: #f9fafc;
      border-radius: 6px;
      padding: 15px;

      .info-title {
        font-weight: 500;
        margin-bottom: 10px;
        font-size: 15px;
        color: #303133;

        i {
          margin-right: 5px;
          color: #409EFF;
        }
      }

      .info-content {
        font-size: 14px;

        &.time-block {
          color: #67c23a;
          font-weight: 500;
        }
      }
    }
  }

  .interviewer-box {
    background: #f9fafc;
    border-radius: 6px;
    padding: 15px;
    margin-bottom: 20px;

    .info-title {
      font-weight: 500;
      margin-bottom: 10px;
      font-size: 15px;
      color: #303133;

      i {
        margin-right: 5px;
        color: #409EFF;
      }
    }

    .info-content {
      display: flex;
      flex-wrap: wrap;
      align-items: center;

      .interviewer-tag {
        margin-right: 8px;
        margin-bottom: 8px;
        padding: 0 10px;
        height: 28px;
        line-height: 26px;
        
        i {
          margin-right: 3px;
        }
      }

      .empty-text {
        color: #909399;
        font-style: italic;
      }
    }
  }

  .notes-box {
    background: #f9fafc;
    border-radius: 6px;
    padding: 15px;
    margin-bottom: 5px;

    .info-title {
      font-weight: 500;
      margin-bottom: 10px;
      font-size: 15px;
      color: #303133;

      i {
        margin-right: 5px;
        color: #409EFF;
      }
    }

    .info-content {
      .notes-content {
        white-space: pre-wrap;
        padding: 8px 12px;
        min-height: 40px;
        color: #606266;
        background: white;
        border-radius: 4px;
        border-left: 3px solid #dcdfe6;
      }
    }
  }

  .detail-actions {
    margin-top: 25px;
    text-align: center;
    border-top: 1px solid #ebeef5;
    padding-top: 20px;
    
    .el-button {
      padding: 8px 20px;
      margin: 0 10px;
      
      i {
        margin-right: 5px;
      }
    }
  }
}

.candidate-detail-dialog {
  .candidate-detail-container {
    min-height: 200px;
    padding: 0;
  }
}
</style>
