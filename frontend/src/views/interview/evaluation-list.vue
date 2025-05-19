<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.search"
        placeholder="搜索候选人或职位"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select
        v-model="listQuery.status"
        placeholder="状态"
        clearable
        style="width: 120px"
        class="filter-item"
        @change="handleFilter"
      >
        <el-option
          v-for="item in statusOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select
        v-model="listQuery.type"
        placeholder="面试类型"
        clearable
        style="width: 120px"
        class="filter-item"
        @change="handleFilter"
      >
        <el-option
          v-for="item in typeOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-button
        v-waves
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >
        搜索
      </el-button>
      <el-button
        class="filter-item"
        type="info"
        icon="el-icon-refresh"
        @click="refreshList"
      >
        刷新
      </el-button>
    </div>

    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="待评估" name="pending">
        <el-table
          :key="tableKey"
          v-loading="listLoading"
          :data="list"
          border
          fit
          highlight-current-row
          style="width: 100%;"
        >
          <el-table-column label="候选人" align="center" min-width="110px">
            <template slot-scope="{row}">
              <span>{{ row.resumeTitle }}</span>
            </template>
          </el-table-column>
          <el-table-column label="应聘职位" align="center" min-width="120px">
            <template slot-scope="{row}">
              <span>{{ row.jobTitle }}</span>
            </template>
          </el-table-column>
          <el-table-column label="面试类型" align="center" width="100px">
            <template slot-scope="{row}">
              <el-tag :type="getInterviewTypeTag(row.interviewType)">
                {{ getInterviewTypeText(row.interviewType) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="面试时间" align="center" width="160px">
            <template slot-scope="{row}">
              <span>{{ formatDateTime(row.scheduleTime) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" align="center" width="100px">
            <template slot-scope="{row}">
              <el-tag :type="getInterviewStatusType(row.status)">
                {{ getInterviewStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="面试官" align="center" min-width="130px">
            <template slot-scope="{row}">
              <el-tag
                v-for="interviewer in row.interviewers"
                :key="interviewer.id"
                size="mini"
                style="margin-right: 5px"
              >
                {{ interviewer.name || interviewer.username }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="180px" class-name="small-padding fixed-width">
            <template slot-scope="{row}">
              <el-button
                v-if="row.status === 'completed'"
                type="primary"
                size="mini"
                @click="handleEvaluate(row)"
              >
                进行评估
              </el-button>
              <el-button
                v-if="row.status === 'evaluated'"
                type="success"
                size="mini"
                @click="handleViewEvaluation(row)"
              >
                查看评估
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="total > 0"
          :total="total"
          :page.sync="listQuery.page"
          :limit.sync="listQuery.limit"
          @pagination="fetchInterviewList"
        />
      </el-tab-pane>

      <el-tab-pane label="已评估" name="evaluated">
        <el-table
          :key="tableKey"
          v-loading="listLoading"
          :data="list"
          border
          fit
          highlight-current-row
          style="width: 100%;"
        >
          <el-table-column label="候选人" align="center" min-width="110px">
            <template slot-scope="{row}">
              <span>{{ row.candidateName }}</span>
            </template>
          </el-table-column>
          <el-table-column label="应聘职位" align="center" min-width="120px">
            <template slot-scope="{row}">
              <span>{{ row.candidatePosition }}</span>
            </template>
          </el-table-column>
          <el-table-column label="面试类型" align="center" width="100px">
            <template slot-scope="{row}">
              <el-tag :type="getInterviewTypeTag(row.type)">
                {{ getInterviewTypeText(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="评估结果" align="center" width="100px">
            <template slot-scope="{row}">
              <el-tag :type="getEvaluationResultType(row.evaluation && row.evaluation.result)" v-if="row.evaluation">
                {{ getEvaluationResultText(row.evaluation && row.evaluation.result) }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="评估分数" align="center" width="100px">
            <template slot-scope="{row}">
              <el-rate
                v-if="row.evaluation && row.evaluation.overall_score"
                v-model="row.evaluation.overall_score"
                disabled
                show-score
                text-color="#ff9900"
              />
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="评估时间" align="center" width="160px">
            <template slot-scope="{row}">
              <span>{{ (row.evaluation && formatDateTime(row.evaluation.created_at)) || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="180px" class-name="small-padding fixed-width">
            <template slot-scope="{row}">
              <el-button
                type="success"
                size="mini"
                @click="handleViewEvaluation(row)"
              >
                查看评估
              </el-button>
              <el-button
                type="warning"
                size="mini"
                @click="handleEditEvaluation(row)"
                v-if="canEdit"
              >
                编辑评估
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="total > 0"
          :total="total"
          :page.sync="listQuery.page"
          :limit.sync="listQuery.limit"
          @pagination="fetchInterviewList"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import Pagination from '@/components/Pagination'
import waves from '@/directive/waves'

export default {
  name: 'InterviewEvaluationList',
  components: {
    Pagination
  },
  directives: {
    waves
  },
  data() {
    return {
      tableKey: 0,
      list: [],
      total: 0,
      listLoading: false,
      activeTab: 'pending',
      listQuery: {
        page: 1,
        limit: 10,
        search: '',
        status: '',
        type: ''
      },
      statusOptions: [
        { label: '待面试', value: 'scheduled' },
        { label: '进行中', value: 'in_progress' },
        { label: '已完成', value: 'completed' },
        { label: '已评估', value: 'evaluated' }
      ],
      typeOptions: [
        { label: '初试', value: 'first' },
        { label: '复试', value: 'second' },
        { label: '终试', value: 'final' }
      ]
    }
  },
  computed: {
    ...mapGetters([
      'roles'
    ]),
    canEdit() {
      // 只有管理员和HR可以编辑评估
      const allowedRoles = ['admin', 'tenant_admin', 'tenant_hr']
      return this.roles.some(role => allowedRoles.includes(role))
    }
  },
  created() {
    this.fetchInterviewList()
  },
  methods: {
    ...mapActions('interview', [
      'getInterviewList'
    ]),
    async fetchInterviewList() {
      this.listLoading = true
      try {
        // 根据activeTab设置查询状态
        let query = { ...this.listQuery }
        if (this.activeTab === 'pending') {
          query.status = 'completed'
        } else if (this.activeTab === 'evaluated') {
          query.status = 'evaluated'
        }

        const response = await this.getInterviewList(query)
        this.list = response || []
        this.total = response.length || 0
      } catch (error) {
        console.error('获取面试列表失败:', error)
        this.$message.error('获取面试列表失败')
      } finally {
        this.listLoading = false
      }
    },
    handleTabClick() {
      this.listQuery.page = 1
      this.fetchInterviewList()
    },
    handleFilter() {
      this.listQuery.page = 1
      this.fetchInterviewList()
    },
    refreshList() {
      this.listQuery = {
        page: 1,
        limit: 10,
        search: '',
        status: '',
        type: ''
      }
      this.fetchInterviewList()
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
    getInterviewStatusText(status) {
      const statusMap = {
        scheduled: '待面试',
        in_progress: '进行中',
        completed: '已完成',
        evaluated: '已评估',
        cancelled: '已取消'
      }
      return statusMap[status] || status
    },
    getInterviewStatusType(status) {
      const typeMap = {
        scheduled: 'info',
        in_progress: 'warning',
        completed: 'success',
        evaluated: 'success',
        cancelled: 'danger'
      }
      return typeMap[status] || 'info'
    },
    getEvaluationResultText(result) {
      const resultMap = {
        'pass': '通过',
        'fail': '不通过',
        'pending': '待定',
        '通过': '通过',
        '不通过': '不通过',
        '待定': '待定'
      }
      return resultMap[result] || result || '-'
    },
    getEvaluationResultType(result) {
      const typeMap = {
        'pass': 'success',
        'fail': 'danger',
        'pending': 'warning',
        '通过': 'success',
        '不通过': 'danger',
        '待定': 'warning'
      }
      return typeMap[result] || 'info'
    },
    handleEvaluate(row) {
      this.$router.push(`/interview/evaluation/${row.id}`)
    },
    handleViewEvaluation(row) {
      this.$router.push(`/interview/view-evaluation/${row.id}`)
    },
    handleEditEvaluation(row) {
      this.$router.push(`/interview/evaluation/${row.id}?edit=true`)
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.filter-container {
  padding-bottom: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-item {
  margin-bottom: 10px;
}

.el-select {
  max-width: 200px;
}
</style> 