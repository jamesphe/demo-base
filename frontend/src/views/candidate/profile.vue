<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span class="page-title">候选人管理</span>
      </div>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="候选人姓名">
          <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable size="small" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="searchForm.phone" placeholder="请输入电话" clearable size="small" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="searchForm.email" placeholder="请输入邮箱" clearable size="small" />
        </el-form-item>
        <el-form-item label="候选人状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable size="small">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="searchForm.dateRange"
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
          <el-button-group>
            <el-button size="small" type="primary" :disabled="selectedCandidates.length === 0" @click="handleBatchUpdateStatus('待筛选')">批量设为待筛选</el-button>
            <el-button size="small" type="success" :disabled="selectedCandidates.length === 0" @click="handleBatchUpdateStatus('面试中')">批量设为面试中</el-button>
            <el-button size="small" type="warning" :disabled="selectedCandidates.length === 0" @click="handleBatchUpdateStatus('已拒绝')">批量设为已拒绝</el-button>
          </el-button-group>
          <span class="selected-count" v-if="selectedCandidates.length > 0">已选择 {{ selectedCandidates.length }} 项</span>
        </div>

        <!-- 操作按钮 -->
        <div class="operation-container">
          <el-button class="filter-item" type="primary" size="small" icon="el-icon-plus" @click="handleCreate">新增候选人</el-button>
          <el-button class="filter-item" type="success" size="small" icon="el-icon-upload2">导入候选人</el-button>
          <el-button class="filter-item" type="info" size="small" icon="el-icon-download">导出数据</el-button>
        </div>
      </div>

      <!-- 候选人列表 -->
      <el-table
        v-loading="listLoading"
        :data="candidates"
        border
        fit
        highlight-current-row
        class="candidate-table"
        @sort-change="handleSortChange"
        @selection-change="handleSelectionChange"
        :header-cell-style="{background:'#f5f7fa', color:'#606266', fontWeight: 'bold'}"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="ID" prop="id" width="70" align="center" sortable="custom" />
        <el-table-column label="姓名" prop="name" min-width="120" align="center" sortable="custom">
          <template slot-scope="{row}">
            <div class="name-cell">
              <el-link 
                type="primary" 
                :underline="false" 
                @click="row.resumeId ? handleViewResumeDetail(row) : handleView(row)"
              >
                {{ row.name }}
              </el-link>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="联系电话" prop="phone" min-width="120" align="center" />
        <el-table-column label="邮箱" prop="email" min-width="180" align="center" show-overflow-tooltip />
        <el-table-column label="简历" prop="resumeName" min-width="100" align="center">
          <template slot-scope="{row}">
            <el-link v-if="row.resumeUrl" type="primary" :href="row.resumeUrl" target="_blank">
              <i class="el-icon-document" /> 查看
            </el-link>
            <el-link v-else-if="row.resumeName" type="info" @click="handlePreviewResume(row)">
              <i class="el-icon-document" /> {{ row.resumeName }}
            </el-link>
            <span v-else>无</span>
          </template>
        </el-table-column>
        <el-table-column label="职位" width="150" align="center">
          <template slot-scope="{row}">
            <el-link v-if="row.jobTitle && row.jobId" type="primary" :underline="false" @click="handleViewJob(row)">
              {{ row.jobTitle }}
            </el-link>
            <el-tag v-else-if="row.jobTitle" size="medium" type="info">{{ row.jobTitle }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="100" align="center" sortable="custom">
          <template slot-scope="{row}">
            <el-tag
              :type="getStatusType(row.status)"
              :class="['status-tag', row.status]"
              effect="light"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="createdAt" width="150" align="center" sortable="custom">
          <template slot-scope="{row}">
            <span class="created-time">{{ formatDateTime(row.createdAt) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" prop="updatedAt" width="150" align="center" sortable="custom">
          <template slot-scope="{row}">
            <span class="updated-time">{{ formatDateTime(row.updatedAt) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="备注" prop="notes" min-width="120" align="center" show-overflow-tooltip>
          <template slot-scope="{row}">
            <el-popover
              v-if="row.notes"
              placement="top"
              width="300"
              trigger="hover"
            >
              <div class="notes-content">{{ row.notes }}</div>
              <el-button slot="reference" type="text">查看备注</el-button>
            </el-popover>
            <span v-else>无</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="230" fixed="right" class-name="action-column">
          <template slot-scope="{row}">
            <div class="action-buttons">
              <el-button size="mini" type="primary" plain class="action-btn" @click="row.resumeId ? handleViewResumeDetail(row) : handleView(row)">
                <i class="el-icon-view" />{{ row.resumeId ? '查看简历' : '查看' }}
              </el-button>
              <el-button size="mini" type="success" plain class="action-btn" @click="handleEdit(row)">
                <i class="el-icon-edit" />编辑
              </el-button>
              <el-button size="mini" type="danger" plain class="action-btn" @click="handleDelete(row)">
                <i class="el-icon-delete" />删除
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

    <!-- 新增/编辑候选人对话框 -->
    <el-dialog :title="dialogStatus === 'create' ? '新增候选人' : '编辑候选人'" :visible.sync="dialogVisible" width="600px">
      <el-form ref="dataForm" :model="temp" :rules="rules" label-position="right" label-width="100px" style="width: 90%; margin: 0 auto;">
        <el-form-item label="租户ID" prop="tenantId">
          <el-input v-model.number="temp.tenantId" type="number" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="temp.name" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="temp.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="temp.email" />
        </el-form-item>
        <el-form-item label="简历链接" prop="resumeUrl">
          <el-input v-model="temp.resumeUrl" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="temp.status" placeholder="请选择状态">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位ID" prop="jobId">
          <el-input v-model.number="temp.jobId" type="number" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="temp.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogStatus === 'create' ? createCandidate() : updateCandidate()">确认</el-button>
      </div>
    </el-dialog>

    <!-- 查看候选人详情对话框 -->
    <el-dialog title="候选人详情" :visible.sync="detailDialogVisible" width="65%" custom-class="candidate-detail-dialog">
      <div v-loading="detailLoading">
        <el-card class="box-card">
          <div slot="header" class="card-header">
            <span>基本信息</span>
          </div>
          <el-row v-if="currentCandidate" :gutter="20">
            <el-col :span="8">
              <div class="info-item">
                <label>ID：</label>
                {{ currentCandidate.id || '-' }}
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>租户ID：</label>
                {{ currentCandidate.tenantId || '-' }}
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>姓名：</label>
                {{ currentCandidate.name || '-' }}
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>联系电话：</label>
                {{ currentCandidate.phone || '-' }}
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>邮箱：</label>
                {{ currentCandidate.email || '-' }}
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>职位名称：</label>
                <template v-if="currentCandidate.jobTitle && currentCandidate.jobId">
                  <el-link type="primary" :underline="false" @click="handleViewJob(currentCandidate)">
                    {{ currentCandidate.jobTitle }}
                  </el-link>
                </template>
                <span v-else>{{ currentCandidate.jobTitle || '-' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>状态：</label>
                <el-tag v-if="currentCandidate.status" :type="getStatusType(currentCandidate.status)">
                  {{ currentCandidate.status }}
                </el-tag>
                <span v-else>-</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>创建时间：</label>
                {{ formatDateTime(currentCandidate.createdAt) || '-' }}
              </div>
            </el-col>
            <el-col :span="8">
              <div class="info-item">
                <label>更新时间：</label>
                {{ formatDateTime(currentCandidate.updatedAt) || '-' }}
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card class="box-card">
          <div slot="header" class="card-header">
            <span>简历信息</span>
          </div>
          <div class="resume-section">
            <div v-if="currentCandidate && currentCandidate.resumeUrl" class="resume-link">
              <el-link type="primary" :href="currentCandidate.resumeUrl" target="_blank">
                <i class="el-icon-document" /> 查看候选人简历
              </el-link>
            </div>
            <div v-else-if="currentCandidate && currentCandidate.resumeName" class="resume-link">
              <el-link type="primary" @click="handlePreviewResume(currentCandidate)">
                <i class="el-icon-document" /> {{ currentCandidate.resumeName }}
              </el-link>
            </div>
            <div v-else class="no-resume">
              <i class="el-icon-warning-outline" /> 暂无简历信息
            </div>
          </div>
          <div v-if="currentCandidate && currentCandidate.resumeId" class="resume-detail-btn-container">
            <el-button type="primary" @click="handleViewResumeDetail(currentCandidate)">
              <i class="el-icon-view" /> 查看简历详情
            </el-button>
          </div>
        </el-card>

        <el-card v-if="currentCandidate && currentCandidate.notes" class="box-card">
          <div slot="header" class="card-header">
            <span>备注信息</span>
          </div>
          <div class="notes-section">
            <p class="notes-content">{{ currentCandidate.notes }}</p>
          </div>
        </el-card>

        <el-card class="box-card">
          <div slot="header" class="card-header">
            <span>面试记录</span>
          </div>
          <div class="interview-section">
            <div v-if="currentCandidate && currentCandidate.interviews && currentCandidate.interviews.length > 0" class="interview-list">
              <el-timeline>
                <el-timeline-item
                  v-for="(interview, index) in currentCandidate.interviews"
                  :key="index"
                  :timestamp="formatDateTime(interview.interviewTime)"
                  placement="top"
                  :color="getInterviewStatusColor(interview.status)"
                >
                  <el-card class="interview-card">
                    <h4>{{ interview.interviewType }} - {{ interview.status }}</h4>
                    <p v-if="interview.interviewer">面试官: {{ interview.interviewer }}</p>
                    <p v-if="interview.location">地点: {{ interview.location }}</p>
                    <p v-if="interview.notes">备注: {{ interview.notes }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
            <div v-else class="no-interviews">
              <i class="el-icon-warning-outline" /> 暂无面试记录
            </div>
          </div>
        </el-card>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button v-if="currentCandidate && currentCandidate.id" type="primary" @click="handleEdit(currentCandidate)">编辑候选人</el-button>
      </div>
    </el-dialog>

    <!-- 批量更新状态确认对话框 -->
    <el-dialog title="批量更新状态" :visible.sync="batchDialogVisible" width="400px">
      <p>确定要将选中的 {{ selectedCandidates.length }} 位候选人状态更新为 "{{ getBatchStatusLabel() }}" 吗？</p>
      <div slot="footer" class="dialog-footer">
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchUpdate">确认</el-button>
      </div>
    </el-dialog>

    <!-- 简历预览弹窗 -->
    <resume-preview
      :visible.sync="resumePreviewVisible"
      :resume-id="currentPreviewId"
      :file-name="currentPreviewFileName"
      @close="handlePreviewClose"
    />

    <!-- 简历详情对话框 -->
    <el-dialog
      title="简历详情"
      :visible.sync="resumeDetailVisible"
      width="70%"
      :before-close="handleResumeDetailClose"
      custom-class="resume-detail-dialog"
    >
      <resume-detail
        :detail="resumeDetail"
        :loading="resumeDetailLoading"
      />
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination'
import { mapGetters, mapActions } from 'vuex'
import { parseTime } from '@/utils/index'
import ResumePreview from '@/components/ResumePreview'
import ResumeDetail from '@/components/ResumeDetail'
import { showJobDetail } from '@/components/JobDetail.vue'

export default {
  name: 'CandidateProfile',
  components: { Pagination, ResumePreview, ResumeDetail },
  filters: {
    statusLabelFilter(status) {
      return status
    }
  },
  data() {
    return {
      listLoading: false,
      listQuery: {
        page: 1,
        limit: 10,
        sortField: '',
        sortOrder: ''
      },
      searchForm: {
        name: '',
        phone: '',
        email: '',
        status: '',
        dateRange: []
      },
      statusOptions: [
        { label: '待筛选', value: '待筛选' },
        { label: '面试中', value: '面试中' },
        { label: '已录用', value: '已录用' },
        { label: '已拒绝', value: '已拒绝' }
      ],
      dialogVisible: false,
      dialogStatus: '',
      temp: {
        id: undefined,
        tenantId: 8,
        name: '',
        email: '',
        phone: '',
        resumeUrl: '',
        status: '待筛选',
        jobId: '',
        notes: ''
      },
      rules: {
        name: [{ required: true, message: '姓名不能为空', trigger: 'blur' }],
        phone: [{ required: true, message: '联系电话不能为空', trigger: 'blur' }],
        email: [{ required: true, message: '邮箱不能为空', trigger: 'blur' }],
        tenantId: [{ required: true, message: '租户ID不能为空', trigger: 'blur' }],
        status: [{ required: true, message: '状态不能为空', trigger: 'change' }]
      },
      detailDialogVisible: false,
      detailLoading: false,
      selectedCandidates: [],
      batchDialogVisible: false,
      batchStatus: null,
      resumePreviewVisible: false,
      currentPreviewId: null,
      currentPreviewFileName: '',
      resumeDetailVisible: false,
      resumeDetailLoading: false,
      resumeDetail: null
    }
  },
  computed: {
    ...mapGetters('candidate', [
      'candidates',
      'total',
      'loading',
      'currentCandidate'
    ]),
    ...mapGetters('resume', [
      'previewUrl',
      'previewLoading'
    ]),
    total() {
      return this.$store.state.candidate.meta?.total || 0
    }
  },
  created() {
    this.getList()
  },
  methods: {
    ...mapActions('candidate', [
      'getCandidateList',
      'addCandidate',
      'updateCandidate',
      'deleteCandidate',
      'getCandidateDetail',
      'createCandidate'
    ]),
    ...mapActions('resume', [
      'getPreviewUrl',
      'getResumeDetail'
    ]),
    formatDateTime(timestamp) {
      if (!timestamp) return ''
      
      // 检查是否是ISO格式的时间字符串
      if (typeof timestamp === 'string' && timestamp.includes('T')) {
        const date = new Date(timestamp)
        if (!isNaN(date.getTime())) {
          return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
          }).replace(/\//g, '-')
        }
      }
      
      return parseTime(timestamp)
    },
    getStatusType(status) {
      const statusMap = {
        '待筛选': 'info',
        '面试中': 'warning',
        '已录用': 'success',
        '已拒绝': 'danger'
      }
      return statusMap[status] || ''
    },
    getInterviewStatusColor(status) {
      const statusMap = {
        '待安排': '#909399',
        '已安排': '#409EFF',
        '已完成': '#67C23A',
        '已取消': '#F56C6C'
      }
      return statusMap[status] || '#909399'
    },
    async getList() {
      this.listLoading = true
      try {
        // 构建查询参数
        const params = {
          page: this.listQuery.page,
          perPage: this.listQuery.limit,
          name: this.searchForm.name || undefined,
          phone: this.searchForm.phone || undefined,
          email: this.searchForm.email || undefined,
          status: this.searchForm.status || undefined,
          startDate: this.searchForm.dateRange && this.searchForm.dateRange[0],
          endDate: this.searchForm.dateRange && this.searchForm.dateRange[1]
        }

        if (this.listQuery.sortField) {
          params.sort_field = this.listQuery.sortField
          params.sort_order = this.listQuery.sortOrder
        }
        
        // 通过Vuex store获取候选人列表
        await this.getCandidateList(params)

      } catch (error) {
        console.error('获取候选人列表失败:', error)
        this.$message.error('获取候选人列表失败')
      }
      this.listLoading = false
    },
    handleSearch() {
      this.listQuery.page = 1
      this.getList()
    },
    resetSearch() {
      this.searchForm = {
        name: '',
        phone: '',
        email: '',
        status: '',
        dateRange: []
      }
      this.listQuery.page = 1
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        tenantId: 8,
        name: '',
        email: '',
        phone: '',
        resumeUrl: '',
        status: '待筛选',
        jobId: '',
        notes: ''
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    async createCandidate() {
      this.$refs['dataForm'].validate(async valid => {
        if (valid) {
          try {
            // 通过Vuex store添加候选人
            await this.createCandidate(this.temp)
            this.dialogVisible = false
            this.getList()
            this.$message({
              type: 'success',
              message: '创建成功'
            })
          } catch (error) {
            console.error('创建候选人失败:', error)
            this.$message.error('创建候选人失败')
          }
        }
      })
    },
    handleEdit(row) {
      this.temp = Object.assign({}, row)
      // 确保字段名称一致
      if (row.tenant_id !== undefined) {
        this.temp.tenantId = row.tenant_id
      }
      if (row.job_id !== undefined) {
        this.temp.jobId = row.job_id
      }
      if (row.resume_url !== undefined) {
        this.temp.resumeUrl = row.resume_url
      }
      
      this.dialogStatus = 'update'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    async updateCandidate() {
      this.$refs['dataForm'].validate(async valid => {
        if (valid) {
          try {
            // 通过Vuex store更新候选人
            await this.updateCandidate(this.temp)
            this.dialogVisible = false
            this.getList()
            this.$message({
              type: 'success',
              message: '更新成功'
            })
          } catch (error) {
            console.error('更新候选人失败:', error)
            this.$message.error('更新候选人失败')
          }
        }
      })
    },
    async handleView(row) {
      this.detailDialogVisible = true
      this.detailLoading = true
      
      try {
        // 通过Vuex store获取候选人详情
        await this.getCandidateDetail(row.id)
      } catch (error) {
        console.error('获取候选人详情失败:', error)
        this.$message.error('获取候选人详情失败')
      } finally {
        this.detailLoading = false
      }
    },
    handleDelete(row) {
      this.$confirm('确认删除该候选人?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          // 通过Vuex store删除候选人
          await this.deleteCandidate(row.id)
          this.getList()
          this.$message({
            type: 'success',
            message: '删除成功'
          })
        } catch (error) {
          console.error('删除候选人失败:', error)
          this.$message.error('删除候选人失败')
        }
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    handleSortChange({ prop, order }) {
      // 处理表格排序
      this.listQuery.sortField = prop
      this.listQuery.sortOrder = order === 'ascending' ? 'asc' : order === 'descending' ? 'desc' : ''
      this.getList()
    },
    handleSelectionChange(selection) {
      this.selectedCandidates = selection
    },
    handleBatchUpdateStatus(status) {
      if (this.selectedCandidates.length === 0) {
        this.$message.warning('请先选择要操作的候选人')
        return
      }
      
      this.batchStatus = status
      this.batchDialogVisible = true
    },
    getBatchStatusLabel() {
      const status = this.statusOptions.find(item => item.value === this.batchStatus)
      return status ? status.label : ''
    },
    async confirmBatchUpdate() {
      try {
        const promises = this.selectedCandidates.map(candidate => 
          this.updateCandidate({
            id: candidate.id,
            status: this.batchStatus
          })
        )
        
        await Promise.all(promises)
        this.$message.success('批量更新状态成功')
        this.batchDialogVisible = false
        this.getList()
      } catch (error) {
        console.error('批量更新状态失败:', error)
        this.$message.error('批量更新状态失败')
      }
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
    handleViewJob(row) {
      if (!row.jobId) {
        this.$message.warning('职位ID不存在')
        return
      }
      
      // 使用JobDetail组件的showJobDetail方法来显示职位详情
      showJobDetail(this, row.jobId, '职位详情')
    },
    async handleViewResumeDetail(row) {
      if (!row.resumeId) {
        this.$message.warning('该候选人没有关联简历')
        return
      }
      
      this.resumeDetailVisible = true
      this.resumeDetailLoading = true
      
      try {
        console.log('开始获取简历详情，简历ID:', row.resumeId)
        const detail = await this.getResumeDetail(row.resumeId)
        console.log('获取简历详情成功:', detail)
        
        // 检查数据是否有效
        if (!detail) {
          throw new Error('获取简历详情失败：数据为空')
        }
        
        this.resumeDetail = detail
      } catch (error) {
        console.error('获取简历详情失败:', error)
        this.$message.error('获取简历详情失败，请稍后重试')
        this.resumeDetailVisible = false
      } finally {
        this.resumeDetailLoading = false
      }
    },
    handleResumeDetailClose() {
      console.log('关闭简历详情对话框')
      this.resumeDetailVisible = false
      this.resumeDetail = null
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
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
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.batch-operations {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  
  .el-button-group {
    margin-right: 15px;
  }
  
  .selected-count {
    color: #606266;
    font-size: 14px;
  }
}

.operation-container {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  
  .filter-item {
    padding: 8px 15px;
  }
}

.candidate-table {
  margin-bottom: 20px;
  border-radius: 4px;
  overflow: hidden;
  
  ::v-deep .el-table__header-wrapper {
    th {
      height: 50px;
      padding: 4px 0;
    }
  }
  
  ::v-deep .el-table__row {
    height: 55px;
  }
  
  .created-time, .updated-time {
    color: #909399;
    font-size: 13px;
  }

  .status-tag {
    text-align: center;
    min-width: 65px;
  }

  .notes-content {
    max-height: 200px;
    overflow-y: auto;
    line-height: 1.6;
    white-space: pre-line;
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

.name-cell {
  display: flex;
  justify-content: center;
}

.resume-detail-btn-container {
  margin-top: 15px;
  display: flex;
  justify-content: center;
}

.candidate-detail-dialog {
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

  .resume-section, .notes-section, .interview-section {
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .interview-list {
    width: 100%;
    
    .interview-card {
      margin-bottom: 10px;
      
      h4 {
        margin-top: 0;
        margin-bottom: 12px;
        font-size: 15px;
        color: #303133;
      }
      
      p {
        margin: 5px 0;
        font-size: 13px;
        color: #606266;
      }
    }
  }

  .resume-link {
    i {
      margin-right: 5px;
    }
  }

  .no-resume, .no-interviews {
    color: #909399;
    font-size: 14px;
    display: flex;
    align-items: center;

    i {
      margin-right: 10px;
      font-size: 16px;
    }
  }

  .notes-content {
    line-height: 1.8;
    white-space: pre-line;
    color: #606266;
    padding: 15px;
    background: #f5f7fa;
    border-radius: 4px;
    width: 100%;
  }
}

.resume-detail-dialog {
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

  .resume-section, .notes-section, .interview-section {
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .interview-list {
    width: 100%;
    
    .interview-card {
      margin-bottom: 10px;
      
      h4 {
        margin-top: 0;
        margin-bottom: 12px;
        font-size: 15px;
        color: #303133;
      }
      
      p {
        margin: 5px 0;
        font-size: 13px;
        color: #606266;
      }
    }
  }

  .resume-link {
    i {
      margin-right: 5px;
    }
  }

  .no-resume, .no-interviews {
    color: #909399;
    font-size: 14px;
    display: flex;
    align-items: center;

    i {
      margin-right: 10px;
      font-size: 16px;
    }
  }

  .notes-content {
    line-height: 1.8;
    white-space: pre-line;
    color: #606266;
    padding: 15px;
    background: #f5f7fa;
    border-radius: 4px;
    width: 100%;
  }
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
</style>
