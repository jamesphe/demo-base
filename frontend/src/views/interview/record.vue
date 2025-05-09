<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>面试记录</span>
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

      <!-- 面试记录列表 -->
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

        <!-- 评估结果 -->
        <el-table-column
          label="评估结果"
          prop="evaluation"
          align="center"
          width="120"
        >
          <template slot-scope="scope">
            <el-tag
              v-if="scope.row.evaluation"
              :type="getEvaluationType(scope.row.evaluation.result)"
            >
              {{ getEvaluationText(scope.row.evaluation.result) }}
            </el-tag>
            <span v-else>-</span>
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
              @click="handleView(scope.row)"
            >查看</el-button>
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

    <!-- 面试详情对话框 -->
    <el-dialog
      title="面试详情"
      :visible.sync="detailDialogVisible"
      width="800px"
      class="interview-detail-dialog"
    >
      <div v-loading="detailLoading">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="面试ID">{{ currentInterview.id }}</el-descriptions-item>
          <el-descriptions-item label="面试类型">
            <el-tag :type="getInterviewTypeTag(currentInterview.type)">
              {{ getInterviewTypeText(currentInterview.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="候选人">{{ currentInterview.candidateName }}</el-descriptions-item>
          <el-descriptions-item label="应聘职位">{{ currentInterview.candidatePosition }}</el-descriptions-item>
          <el-descriptions-item label="面试时间">{{ formatDateTime(currentInterview.time) }}</el-descriptions-item>
          <el-descriptions-item label="面试地点">{{ currentInterview.location }}</el-descriptions-item>
          <el-descriptions-item label="面试官">
            <el-tag
              v-for="interviewer in currentInterview.interviewers"
              :key="interviewer.id"
              size="mini"
              class="interviewer-tag"
            >
              {{ interviewer.name }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentInterview.status)">
              {{ getStatusText(currentInterview.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ currentInterview.notes || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 评估结果 -->
        <div v-if="currentInterview.evaluation" class="evaluation-section">
          <h3>评估结果</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="评估结果">
              <el-tag :type="getEvaluationType(currentInterview.evaluation.result)">
                {{ getEvaluationText(currentInterview.evaluation.result) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="评估时间">
              {{ formatDateTime(currentInterview.evaluation.time) }}
            </el-descriptions-item>
            <el-descriptions-item label="技术能力评分">
              <el-rate
                v-model="currentInterview.evaluation.technicalScore"
                disabled
                show-score
                text-color="#ff9900"
              />
            </el-descriptions-item>
            <el-descriptions-item label="沟通能力评分">
              <el-rate
                v-model="currentInterview.evaluation.communicationScore"
                disabled
                show-score
                text-color="#ff9900"
              />
            </el-descriptions-item>
            <el-descriptions-item label="综合评分">
              <el-rate
                v-model="currentInterview.evaluation.overallScore"
                disabled
                show-score
                text-color="#ff9900"
              />
            </el-descriptions-item>
            <el-descriptions-item label="评估人">
              {{ currentInterview.evaluation.evaluator }}
            </el-descriptions-item>
            <el-descriptions-item label="评估意见" :span="2">
              {{ currentInterview.evaluation.comments }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import Pagination from '@/components/Pagination'
import { getInterviewerList, getInterviewDetail } from '@/api/interview'

export default {
  name: 'InterviewRecord',
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
      interviewerOptions: [],
      detailDialogVisible: false,
      detailLoading: false,
      currentInterview: {}
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
      'updateInterview'
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
        this.interviewerOptions = response.data
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
    async handleView(row) {
      this.detailDialogVisible = true
      this.detailLoading = true
      try {
        const response = await getInterviewDetail(row.id)
        this.currentInterview = response.data
      } catch (error) {
        console.error('获取面试详情失败:', error)
        this.$message.error('获取面试详情失败')
      } finally {
        this.detailLoading = false
      }
    },
    handleEdit(row) {
      this.$router.push(`/interview/schedule?id=${row.id}`)
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
    handleEvaluate(row) {
      this.$router.push(`/interview/evaluation/${row.id}`)
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
    getEvaluationText(result) {
      const resultMap = {
        pass: '通过',
        fail: '不通过',
        pending: '待定'
      }
      return resultMap[result] || '未评估'
    },
    getEvaluationType(result) {
      const typeMap = {
        pass: 'success',
        fail: 'danger',
        pending: 'warning'
      }
      return typeMap[result] || 'info'
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

.interview-detail-dialog {
  ::v-deep .el-dialog__body {
    padding: 20px;
  }

  .evaluation-section {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;

    h3 {
      margin: 0 0 20px;
      font-size: 16px;
      color: #303133;
    }
  }
}

::v-deep .el-descriptions {
  margin-bottom: 20px;

  .el-descriptions-item__label {
    width: 120px;
    font-weight: 500;
  }
}
</style>
