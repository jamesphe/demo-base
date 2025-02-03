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
        <el-slider
          v-model="matchRateFilter"
          :min="60"
          :max="100"
          style="width: 200px; margin-left: 20px"
          class="filter-item"
          @change="handleMatchRateChange"
        >
          <template #default>
            <span>匹配度：{{ matchRateFilter }}%</span>
          </template>
        </el-slider>
      </div>

      <el-table
        v-loading="listLoading"
        :data="list"
        border
      >
        <el-table-column label="候选人" prop="name" />
        <el-table-column label="工作年限" prop="workYears">
          <template #default="{ row }">
            {{ row.workYears }}年
          </template>
        </el-table-column>
        <el-table-column label="学历" prop="education.degree" />
        <el-table-column label="当前状态" prop="jobIntention.jobStatus" />
        <el-table-column label="匹配度">
          <template #default="{ row }">
            <el-progress :percentage="row.matchRate" :color="customColorMethod" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="success" size="mini" @click="handleView(row)">查看</el-button>
            <el-button type="primary" size="mini" @click="handleContact(row)">联系</el-button>
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

    <el-dialog title="候选人详情" :visible.sync="dialogVisible" width="60%">
      <div v-loading="detailLoading">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ detail.name }}</el-descriptions-item>
          <el-descriptions-item label="工作年限">{{ detail.workYears }}年</el-descriptions-item>
          <el-descriptions-item label="学历">{{ detail.education && detail.education.degree }}</el-descriptions-item>
          <el-descriptions-item label="专业">{{ detail.education && detail.education.major }}</el-descriptions-item>
          <el-descriptions-item label="毕业院校">{{ detail.education && detail.education.school }}</el-descriptions-item>
          <el-descriptions-item label="期望薪资">{{ detail.salary && detail.salary.expected }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">技能匹配</div>
        <el-table :data="detail.skillMatches" border size="small">
          <el-table-column label="技能" prop="name" />
          <el-table-column label="掌握程度" prop="matchLevel" />
          <el-table-column label="使用年限" prop="yearOfExperience">
            <template #default="{ row }">{{ row.yearOfExperience }}年</template>
          </el-table-column>
        </el-table>

        <div class="section-title">工作经历</div>
        <el-timeline>
          <el-timeline-item
            v-for="(work, index) in detail.workExperience"
            :key="index"
            :timestamp="work.period"
            placement="top"
          >
            <el-card>
              <h4>{{ work.company }} - {{ work.position }}</h4>
              <p>{{ work.description }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <div class="section-title">项目经验</div>
        <el-collapse>
          <el-collapse-item
            v-for="(project, index) in detail.projects"
            :key="index"
            :title="project.name"
          >
            <div>
              <p><strong>角色：</strong>{{ project.role }}</p>
              <p><strong>描述：</strong>{{ project.description }}</p>
              <p><strong>技术栈：</strong>{{ project.technologies.join('、') }}</p>
            </div>
          </el-collapse-item>
        </el-collapse>

        <div class="section-title">求职意向</div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="期望职位">{{ detail.jobIntention && detail.jobIntention.positions ? detail.jobIntention.positions.join('、') : '' }}</el-descriptions-item>
          <el-descriptions-item label="期望城市">{{ detail.jobIntention && detail.jobIntention.cities ? detail.jobIntention.cities.join('、') : '' }}</el-descriptions-item>
          <el-descriptions-item label="到岗时间">{{ detail.jobIntention && detail.jobIntention.availableTime }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">{{ detail.jobIntention && detail.jobIntention.jobStatus }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">加分项</div>
        <el-tag
          v-for="item in detail.highlights"
          :key="item"
          style="margin-right: 10px"
        >
          {{ item }}
        </el-tag>

        <div class="section-title">推荐理由</div>
        <p>{{ detail.recommendReason }}</p>
      </div>
    </el-dialog>

    <el-dialog title="联系方式" :visible.sync="contactVisible" width="30%">
      <div v-loading="contactLoading">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="手机号码">{{ contactInfo.phone }}</el-descriptions-item>
          <el-descriptions-item label="电子邮箱">{{ contactInfo.email }}</el-descriptions-item>
          <el-descriptions-item label="微信号">{{ contactInfo.wechat }}</el-descriptions-item>
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
        limit: 10,
        positionId: undefined,
        matchRate: 60
      },
      matchRateFilter: 60,
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
    handleMatchRateChange(value) {
      this.listQuery.matchRate = value
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
  padding-bottom: 20px;
  display: flex;
  align-items: center;
  .filter-item {
    margin-right: 10px;
  }
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin: 20px 0 10px;
  padding-left: 10px;
  border-left: 4px solid #409EFF;
}

.el-timeline {
  margin: 20px 0;
}

.el-collapse {
  margin: 20px 0;
}

.el-tag {
  margin: 5px;
}
</style> 