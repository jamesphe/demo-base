<template>
  <div class="app-container">
    <el-card>
      <!-- 搜索栏 -->
      <div class="filter-container">
        <el-input
          v-model="listQuery.name"
          placeholder="候选人姓名"
          style="width: 200px;"
          class="filter-item"
        />
        <el-select
          v-model="listQuery.status"
          placeholder="评估状态"
          clearable
          style="width: 120px"
          class="filter-item"
        >
          <el-option
            v-for="item in statusOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
          搜索
        </el-button>
      </div>

      <!-- 评估列表 -->
      <el-table
        :data="list"
        border
        style="width: 100%"
        v-loading="listLoading"
      >
        <el-table-column label="候选人" prop="candidateName" />
        <el-table-column label="面试环节" prop="interviewRound" width="100" />
        <el-table-column label="技术能力" width="200">
          <template slot-scope="{row}">
            <el-rate
              v-model="row.technicalScore"
              disabled
              show-score
              text-color="#ff9900"
            />
          </template>
        </el-table-column>
        <el-table-column label="沟通能力" width="200">
          <template slot-scope="{row}">
            <el-rate
              v-model="row.communicationScore"
              disabled
              show-score
              text-color="#ff9900"
            />
          </template>
        </el-table-column>
        <el-table-column label="综合评价" prop="overallRating">
          <template slot-scope="{row}">
            <el-tag :type="row.overallRating | ratingTypeFilter">
              {{ row.overallRating }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="面试官" width="150">
          <template slot-scope="{row}">
            <div>{{ row.evaluator }}</div>
            <div class="text-muted">{{ row.evaluatorTitle }}</div>
          </template>
        </el-table-column>
        <el-table-column label="评估时间" prop="evaluationTime" width="180" />
        <el-table-column label="操作" align="center" width="180">
          <template slot-scope="{row}">
            <el-button size="mini" type="primary" @click="handleEvaluate(row)">评估</el-button>
            <el-button size="mini" type="success" @click="handleView(row)">查看</el-button>
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

    <!-- 评估详情对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="65%">
      <div v-loading="detailLoading">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="候选人">{{ detail.candidateName }}</el-descriptions-item>
          <el-descriptions-item label="面试环节">{{ detail.interviewRound }}</el-descriptions-item>
          <el-descriptions-item label="面试时长">{{ detail.duration }}</el-descriptions-item>
          <el-descriptions-item label="评估状态">
            <el-tag :type="detail.status | statusTypeFilter">{{ detail.status }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 技术评估 -->
        <div class="evaluation-section">
          <h3>技术评估</h3>
          <el-table :data="detail.technicalItems" border size="small">
            <el-table-column label="评估项" prop="name" />
            <el-table-column label="得分" width="180">
              <template slot-scope="{row}">
                <el-rate v-model="row.score" disabled show-score />
              </template>
            </el-table-column>
            <el-table-column label="评价" prop="comment" />
          </el-table>
        </div>

        <!-- 综合素质评估 -->
        <div class="evaluation-section">
          <h3>综合素质评估</h3>
          <el-table :data="detail.softSkills" border size="small">
            <el-table-column label="评估项" prop="name" />
            <el-table-column label="得分" width="180">
              <template slot-scope="{row}">
                <el-rate v-model="row.score" disabled show-score />
              </template>
            </el-table-column>
            <el-table-column label="评价" prop="comment" />
          </el-table>
        </div>

        <!-- 项目经验 -->
        <div class="evaluation-section">
          <h3>项目经验评估</h3>
          <el-table :data="detail.projectExperience" border size="small">
            <el-table-column label="项目名称" prop="name" />
            <el-table-column label="担任角色" prop="role" width="120" />
            <el-table-column label="项目贡献" prop="contribution" />
            <el-table-column label="亮点" prop="highlight" />
          </el-table>
        </div>

        <!-- 综合评价 -->
        <div class="evaluation-section">
          <h3>综合评价</h3>
          <div class="evaluation-tags">
            <el-tag
              v-for="tag in detail.tags"
              :key="tag"
              style="margin-right: 10px"
            >{{ tag }}</el-tag>
          </div>
          <div class="evaluation-comment">{{ detail.comment }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination'
import { getEvaluationList, getEvaluationDetail } from '@/api/candidate'

export default {
  name: 'CandidateEvaluation',
  components: { Pagination },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: false,
      listQuery: {
        page: 1,
        limit: 10,
        name: undefined,
        status: undefined
      },
      statusOptions: [
        { label: '待定', value: 'pending' },
        { label: '通过', value: 'pass' },
        { label: '未通过', value: 'reject' }
      ],
      dialogVisible: false,
      dialogTitle: '',
      detailLoading: false,
      detail: {}
    }
  },
  filters: {
    ratingTypeFilter(rating) {
      const map = {
        '推荐': 'success',
        '待定': 'warning',
        '不推荐': 'danger'
      }
      return map[rating]
    },
    statusTypeFilter(status) {
      const map = {
        '待定': 'warning',
        '通过': 'success',
        '未通过': 'danger'
      }
      return map[status]
    }
  },
  created() {
    this.getList()
  },
  methods: {
    async getList() {
      this.listLoading = true
      try {
        const { data } = await getEvaluationList(this.listQuery)
        this.list = data.items
        this.total = data.total
      } catch (error) {
        console.error('获取评估列表失败:', error)
      }
      this.listLoading = false
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    async handleView(row) {
      this.dialogTitle = '评估详情'
      this.dialogVisible = true
      this.detailLoading = true
      try {
        const { data } = await getEvaluationDetail(row.id)
        this.detail = data
      } catch (error) {
        console.error('获取评估详情失败:', error)
      }
      this.detailLoading = false
    },
    handleEvaluate(row) {
      // TODO: 实现评估功能
    }
  }
}
</script>

<style lang="scss" scoped>
.evaluation-section {
  margin-top: 20px;
  
  h3 {
    margin-bottom: 15px;
    font-weight: 500;
    color: #303133;
  }
}

.evaluation-tags {
  margin-bottom: 15px;
}

.evaluation-comment {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  line-height: 1.6;
}

.text-muted {
  color: #909399;
  font-size: 13px;
}
</style> 