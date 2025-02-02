<template>
  <div class="app-container">
    <el-card>
      <div class="filter-container">
        <el-select
          v-model="selectedPosition"
          placeholder="请选择职位"
          style="width: 200px"
          class="filter-item"
          @change="handlePositionChange"
        >
          <el-option
            v-for="item in positions"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </div>

      <el-table
        v-loading="listLoading"
        :data="list"
        border
      >
        <el-table-column label="候选人" prop="name" />
        <el-table-column label="匹配度">
          <template slot-scope="{row}">
            <el-progress :percentage="row.matchRate" :color="customColorMethod" />
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="{row}">
            <el-button type="success" @click="handleView(row)">查看</el-button>
            <el-button type="primary" @click="handleContact(row)">联系</el-button>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="total>0"
        :total="total"
        :page.sync="listQuery.page"
        :limit.sync="listQuery.limit"
        @pagination="getRecommendations"
      />
    </el-card>

    <el-dialog title="候选人详情" :visible.sync="dialogVisible">
      <div v-loading="detailLoading">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="姓名">{{ detail.name }}</el-descriptions-item>
          <el-descriptions-item label="工作年限">{{ detail.workYears }}年</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <el-dialog title="联系方式" :visible.sync="contactVisible">
      <div v-loading="contactLoading">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="手机号码">{{ contactInfo.phone }}</el-descriptions-item>
          <el-descriptions-item label="电子邮箱">{{ contactInfo.email }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination'
import { getPositionList, getRecommendations, getRecommendationDetail, contactCandidate } from '@/api/candidate'

export default {
  name: 'CandidateRecommendation',
  components: { Pagination },
  data() {
    return {
      selectedPosition: undefined,
      positions: [],
      list: [],
      total: 0,
      listLoading: false,
      listQuery: {
        page: 1,
        limit: 10
      },
      dialogVisible: false,
      detailLoading: false,
      detail: {},
      contactVisible: false,
      contactLoading: false,
      contactInfo: {}
    }
  },
  created() {
    this.getPositions()
  },
  methods: {
    async getPositions() {
      try {
        const { data } = await getPositionList({ status: 'open' })
        this.positions = data.items
      } catch (error) {
        console.error('获取职位列表失败:', error)
      }
    },
    handlePositionChange(positionId) {
      this.listQuery.positionId = positionId
      this.getRecommendations()
    },
    async getRecommendations() {
      if (!this.listQuery.positionId) return
      this.listLoading = true
      try {
        const { data } = await getRecommendations(this.listQuery)
        this.list = data.items
        this.total = data.total
      } catch (error) {
        console.error('获取推荐候选人失败:', error)
      }
      this.listLoading = false
    },
    customColorMethod(percentage) {
      if (percentage > 80) return '#67C23A'
      if (percentage > 60) return '#E6A23C'
      return '#F56C6C'
    },
    async handleView(row) {
      this.dialogVisible = true
      this.detailLoading = true
      try {
        const { data } = await getRecommendationDetail(row.id)
        this.detail = data
      } catch (error) {
        console.error('获取候选人详情失败:', error)
      }
      this.detailLoading = false
    },
    async handleContact(row) {
      this.contactVisible = true
      this.contactLoading = true
      try {
        const { data } = await contactCandidate({ id: row.id, type: 'view' })
        this.contactInfo = data.contact
      } catch (error) {
        console.error('获取联系方式失败:', error)
      }
      this.contactLoading = false
    }
  }
}
</script>

<style lang="scss" scoped>
.filter-container {
  padding-bottom: 10px;
  .filter-item {
    margin-right: 10px;
  }
}

.text-muted {
  color: #909399;
  font-size: 13px;
}
</style> 