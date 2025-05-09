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
          prop="candidateName"
          align="center"
          min-width="120"
        >
          <template slot-scope="scope">
            <div class="candidate-info">
              <span class="candidate-name">{{ scope.row.candidateName }}</span>
              <el-tag size="mini" type="info">{{ scope.row.candidatePosition }}</el-tag>
            </div>
          </template>
        </el-table-column>

        <!-- 面试类型 -->
        <el-table-column
          label="面试类型"
          prop="type"
          align="center"
          width="100"
        >
          <template slot-scope="scope">
            <el-tag :type="getInterviewTypeTag(scope.row.type)">
              {{ getInterviewTypeText(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 面试时间 -->
        <el-table-column
          label="面试时间"
          prop="time"
          align="center"
          width="160"
          sortable="custom"
        >
          <template slot-scope="scope">
            <span>{{ formatDateTime(scope.row.time) }}</span>
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
          prop="interviewers"
          align="center"
          min-width="120"
        >
          <template slot-scope="scope">
            <el-tag
              v-for="interviewer in scope.row.interviewers"
              :key="interviewer.id"
              size="mini"
              class="interviewer-tag"
            >
              {{ interviewer.name }}
            </el-tag>
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
          width="280"
          fixed="right"
        >
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              plain
              class="action-btn"
              @click="handleView(scope.row)"
            >
              <i class="el-icon-view" />
            </el-button>
            <el-button
              size="mini"
              type="success"
              plain
              class="action-btn"
              @click="handlePreparation(scope.row)"
            >
              <i class="el-icon-notebook-2" />
            </el-button>
            <el-button
              size="mini"
              type="success"
              plain
              :disabled="scope.row.status !== 'scheduled'"
              @click="handleEdit(scope.row)"
            >编辑</el-button>
            <el-button
              size="mini"
              type="danger"
              plain
              :disabled="scope.row.status !== 'scheduled'"
              @click="handleCancel(scope.row)"
            >取消</el-button>
            <el-button
              size="mini"
              type="warning"
              plain
              :disabled="scope.row.status !== 'completed'"
              @click="handleEvaluate(scope.row)"
            >评估</el-button>
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
        <el-button type="primary" @click="submitForm" :loading="submitting">
          确 定
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import Pagination from '@/components/Pagination'
import { getInterviewerList } from '@/api/interview'

export default {
  name: 'InterviewSchedule',
  components: {
    Pagination
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
        notes: ''
      },
      interviewRules: {
        type: [
          { required: true, message: '请选择面试类型', trigger: 'change' }
        ],
        time: [
          { required: true, message: '请选择面试时间', trigger: 'change' }
        ],
        interviewers: [
          { required: true, message: '请选择面试官', trigger: 'change' }
        ],
        location: [
          { required: true, message: '请输入面试地点', trigger: 'blur' }
        ]
      },
      interviewerOptions: [],
      submitting: false
    }
  },
  computed: {
    ...mapGetters('interview', [
      'interviewList',
      'total',
      'loading'
    ])
  },
  created() {
    this.getList()
    this.getInterviewers()
  },
  methods: {
    ...mapActions('interview', [
      'getInterviewList',
      'createInterviews',
      'updateInterview',
      'deleteInterview',
      'checkTimeConflict'
    ]),
    async getList() {
      try {
        const params = {
          ...this.listQuery,
          ...this.searchForm,
          timeStart: this.searchForm.timeRange?.[0],
          timeEnd: this.searchForm.timeRange?.[1]
        }
        await this.getInterviewList(params)
      } catch (error) {
        console.error('获取面试列表失败:', error)
        this.$message.error('获取面试列表失败')
      }
    },
    async getInterviewers() {
      try {
        const response = await getInterviewerList()
        this.interviewerOptions = response.map(item => ({
          id: item.id,
          name: item.username
        }))
      } catch (error) {
        console.error('获取面试官列表失败:', error)
        this.$message.error('获取面试官列表失败')
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
        notes: ''
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogType = 'edit'
      this.interviewForm = {
        ...row,
        interviewers: row.interviewers.map(i => i.id)
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
      // TODO: 实现查看面试详情
    },
    handlePreparation(row) {
      this.$router.push(`/interview/preparation/${row.id}`)
    },
    handleEvaluate(row) {
      this.$router.push(`/interview/evaluation/${row.id}`)
    },
    async submitForm() {
      try {
        await this.$refs.interviewForm.validate()
        
        // 检查时间冲突
        const hasConflict = await this.checkTimeConflict({
          time: this.interviewForm.time,
          interviewers: this.interviewForm.interviewers
        })
        
        if (hasConflict) {
          this.$message.warning('所选时间与面试官其他面试时间冲突，请重新选择')
          return
        }

        this.submitting = true
        
        if (this.dialogType === 'add') {
          await this.createInterviews(this.interviewForm)
          this.$message.success('面试创建成功')
        } else {
          await this.updateInterview({
            id: this.interviewForm.id,
            data: this.interviewForm
          })
          this.$message.success('面试更新成功')
        }
        
        this.dialogVisible = false
        this.getList()
      } catch (error) {
        console.error('提交表单失败:', error)
        this.$message.error('提交表单失败')
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
    }
  }
  
  .interviewer-tag {
    margin: 2px;
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
</style>
