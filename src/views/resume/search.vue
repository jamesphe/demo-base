<template>
  <basic-view title="简历检索">
    <div class="search-container">
      <!-- 搜索条件 -->
      <el-form :model="searchForm" ref="searchForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="关键词">
              <el-input 
                v-model="searchForm.keyword" 
                placeholder="支持姓名、技能、公司等"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="工作经验">
              <el-select v-model="searchForm.experience" placeholder="请选择" clearable>
                <el-option label="不限" value="" />
                <el-option label="应届生" value="0" />
                <el-option label="1-3年" value="1-3" />
                <el-option label="3-5年" value="3-5" />
                <el-option label="5-10年" value="5-10" />
                <el-option label="10年以上" value="10+" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学历要求">
              <el-select v-model="searchForm.education" placeholder="请选择" clearable>
                <el-option label="不限" value="" />
                <el-option label="大专" value="college" />
                <el-option label="本科" value="bachelor" />
                <el-option label="硕士" value="master" />
                <el-option label="博士" value="doctor" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="技能标签">
              <el-select
                v-model="searchForm.skills"
                multiple
                filterable
                allow-create
                default-first-option
                placeholder="请选择或输入"
                clearable
              >
                <el-option
                  v-for="item in skillOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="更新时间">
              <el-date-picker
                v-model="searchForm.updateTime"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="yyyy-MM-dd"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="简历来源">
              <el-select v-model="searchForm.source" placeholder="请选择" clearable>
                <el-option label="全部" value="" />
                <el-option label="内部投递" value="internal" />
                <el-option label="招聘网站" value="website" />
                <el-option label="猎头推荐" value="headhunter" />
                <el-option label="员工推荐" value="referral" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">搜索</el-button>
          <el-button @click="resetForm">重置</el-button>
          <el-button type="success" @click="handleExport" :disabled="!resultList.length">导出结果</el-button>
        </el-form-item>
      </el-form>

      <!-- 搜索结果 -->
      <div class="search-result" v-loading="loading">
        <div class="result-header">
          <span class="result-count">共找到 {{ total }} 份简历</span>
          <div class="view-controls">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="list">列表视图</el-radio-button>
              <el-radio-button label="card">卡片视图</el-radio-button>
            </el-radio-group>
            <el-select v-model="sortBy" size="small" style="margin-left: 10px">
              <el-option label="更新时间" value="updateTime" />
              <el-option label="相关度" value="relevance" />
              <el-option label="工作年限" value="experience" />
            </el-select>
          </div>
        </div>

        <!-- 列表视图 -->
        <template v-if="viewMode === 'list'">
          <el-table :data="resultList" style="width: 100%">
            <el-table-column prop="name" label="姓名" width="100">
              <template slot-scope="{row}">
                <el-button type="text" @click="viewDetail(row)">{{ row.name }}</el-button>
              </template>
            </el-table-column>
            <el-table-column prop="age" label="年龄" width="80" />
            <el-table-column prop="education" label="学历" width="100" />
            <el-table-column prop="experience" label="工作经验" width="100" />
            <el-table-column prop="skills" label="技能标签">
              <template slot-scope="{row}">
                <el-tag
                  v-for="skill in row.skills"
                  :key="skill"
                  size="small"
                  style="margin-right: 5px; margin-bottom: 5px"
                >
                  {{ skill }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="updateTime" label="更新时间" width="180">
              <template slot-scope="{row}">
                {{ formatDate(row.updateTime) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template slot-scope="{row}">
                <el-button type="text" @click="viewDetail(row)">查看</el-button>
                <el-button type="text" @click="handleDownload(row)">下载</el-button>
                <el-button 
                  type="text" 
                  :class="{'starred': row.starred}"
                  @click="toggleStar(row)"
                >
                  {{ row.starred ? '取消收藏' : '收藏' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>

        <!-- 卡片视图 -->
        <template v-else>
          <el-row :gutter="20">
            <el-col :span="6" v-for="item in resultList" :key="item.id">
              <el-card class="resume-card" shadow="hover">
                <div class="card-header">
                  <span class="name">{{ item.name }}</span>
                  <el-tag size="small">{{ item.education }}</el-tag>
                </div>
                <div class="card-content">
                  <p>{{ item.age }}岁 | {{ item.experience }}</p>
                  <div class="skills">
                    <el-tag
                      v-for="skill in item.skills"
                      :key="skill"
                      size="mini"
                      style="margin-right: 5px; margin-bottom: 5px"
                    >
                      {{ skill }}
                    </el-tag>
                  </div>
                  <p class="update-time">更新时间：{{ formatDate(item.updateTime) }}</p>
                </div>
                <div class="card-footer">
                  <el-button type="text" @click="viewDetail(item)">查看</el-button>
                  <el-button type="text" @click="handleDownload(item)">下载</el-button>
                  <el-button 
                    type="text" 
                    :class="{'starred': item.starred}"
                    @click="toggleStar(item)"
                  >
                    {{ item.starred ? '取消收藏' : '收藏' }}
                  </el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </template>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            background
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="page.current"
            :page-sizes="[12, 24, 36, 48]"
            :page-size="page.size"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
          />
        </div>
      </div>

      <!-- 简历详情对话框 -->
      <el-dialog
        title="简历详情"
        :visible.sync="detailVisible"
        width="70%"
        :before-close="handleDetailClose"
      >
        <div v-loading="detailLoading">
          <el-descriptions :column="3" border>
            <el-descriptions-item label="姓名">{{ currentDetail.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ currentDetail.gender }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ currentDetail.age }}岁</el-descriptions-item>
            <el-descriptions-item label="学历">{{ currentDetail.education }}</el-descriptions-item>
            <el-descriptions-item label="工作经验">{{ currentDetail.experience }}</el-descriptions-item>
            <el-descriptions-item label="期望薪资">{{ currentDetail.expectedSalary }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ currentDetail.phone }}</el-descriptions-item>
            <el-descriptions-item label="电子邮箱">{{ currentDetail.email }}</el-descriptions-item>
            <el-descriptions-item label="当前状态">{{ currentDetail.status }}</el-descriptions-item>
          </el-descriptions>

          <div class="detail-section">
            <h4>技能标签</h4>
            <div class="skills">
              <el-tag
                v-for="skill in currentDetail.skills"
                :key="skill"
                style="margin-right: 10px; margin-bottom: 10px"
              >
                {{ skill }}
              </el-tag>
            </div>
          </div>

          <div class="detail-section">
            <h4>工作经历</h4>
            <el-timeline>
              <el-timeline-item
                v-for="(work, index) in currentDetail.workExperience"
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
          </div>

          <div class="detail-section">
            <h4>教育经历</h4>
            <el-timeline>
              <el-timeline-item
                v-for="(edu, index) in currentDetail.educationDetail"
                :key="index"
                :timestamp="edu.period"
                placement="top"
              >
                <el-card>
                  <h4>{{ edu.school }} - {{ edu.major }}</h4>
                  <p>{{ edu.degree }}</p>
                  <div v-if="edu.achievements && edu.achievements.length">
                    <p class="achievements-title">主要成就：</p>
                    <ul>
                      <li v-for="(achievement, i) in edu.achievements" :key="i">
                        {{ achievement }}
                      </li>
                    </ul>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>

          <div class="detail-section">
            <h4>项目经历</h4>
            <el-timeline>
              <el-timeline-item
                v-for="(project, index) in currentDetail.projects"
                :key="index"
                :timestamp="project.period"
                placement="top"
              >
                <el-card>
                  <h4>{{ project.name }}</h4>
                  <p>{{ project.description }}</p>
                  <p>主要职责：{{ project.responsibility }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
        </div>
      </el-dialog>
    </div>
  </basic-view>
</template>

<script>
import BasicView from '@/components/BasicView'
import { searchResumes, downloadResume, toggleResumeStar, exportSearchResult } from '@/api/resume'

export default {
  name: 'ResumeSearch',
  components: { BasicView },
  data() {
    return {
      loading: false,
      detailLoading: false,
      searchForm: {
        keyword: '',
        experience: '',
        education: '',
        skills: [],
        updateTime: [],
        source: ''
      },
      skillOptions: [
        { value: 'java', label: 'Java' },
        { value: 'python', label: 'Python' },
        { value: 'javascript', label: 'JavaScript' },
        { value: 'vue', label: 'Vue.js' },
        { value: 'react', label: 'React' },
        { value: 'node', label: 'Node.js' }
      ],
      viewMode: 'list',
      sortBy: 'updateTime',
      resultList: [],
      total: 0,
      page: {
        current: 1,
        size: 12
      },
      detailVisible: false,
      currentDetail: {}
    }
  },
  created() {
    this.handleSearch()
  },
  methods: {
    // 搜索
    async handleSearch() {
      this.loading = true
      try {
        const params = {
          page: this.page.current,
          limit: this.page.size,
          ...this.searchForm,
          sort: this.sortBy
        }
        // 处理日期范围
        if (this.searchForm.updateTime && this.searchForm.updateTime.length === 2) {
          params.startDate = this.searchForm.updateTime[0]
          params.endDate = this.searchForm.updateTime[1]
          delete params.updateTime
        }

        const { data } = await searchResumes(params)
        this.resultList = data.items
        this.total = data.total
      } catch (error) {
        this.$message.error('搜索失败')
      }
      this.loading = false
    },

    // 重置表单
    resetForm() {
      this.$refs.searchForm.resetFields()
      this.handleSearch()
    },

    // 导出结果
    async handleExport() {
      try {
        const params = {
          ...this.searchForm,
          sort: this.sortBy
        }
        const response = await exportSearchResult(params)
        const blob = new Blob([response.data], { type: 'application/vnd.ms-excel' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', '简历搜索结果.xlsx')
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        this.$message.success('导出成功')
      } catch (error) {
        this.$message.error('导出失败')
      }
    },

    // 查看详情
    viewDetail(row) {
      this.detailVisible = true
      this.currentDetail = row
    },

    // 关闭详情
    handleDetailClose() {
      this.detailVisible = false
      this.currentDetail = {}
    },

    // 下载简历
    async handleDownload(row) {
      try {
        const response = await downloadResume(row.id)
        const blob = new Blob([response.data])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', row.fileName)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        this.$message.success('下载成功')
      } catch (error) {
        this.$message.error('下载失败')
      }
    },

    // 收藏/取消收藏
    async toggleStar(row) {
      try {
        await toggleResumeStar(row.id, !row.starred)
        row.starred = !row.starred
        this.$message.success(row.starred ? '已收藏' : '已取消收藏')
      } catch (error) {
        this.$message.error('操作失败')
      }
    },

    // 格式化日期
    formatDate(date) {
      return new Date(date).toLocaleDateString()
    },

    // 分页大小改变
    handleSizeChange(val) {
      this.page.size = val
      this.handleSearch()
    },

    // 当前页改变
    handleCurrentChange(val) {
      this.page.current = val
      this.handleSearch()
    }
  }
}
</script>

<style lang="scss" scoped>
.search-container {
  padding: 20px;

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 20px 0;

    .result-count {
      font-size: 14px;
      color: #606266;
    }
  }

  .resume-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;

      .name {
        font-size: 16px;
        font-weight: 500;
      }
    }

    .card-content {
      min-height: 120px;

      .skills {
        margin: 10px 0;
      }

      .update-time {
        font-size: 12px;
        color: #909399;
        margin-top: 10px;
      }
    }

    .card-footer {
      border-top: 1px solid #EBEEF5;
      padding-top: 10px;
      text-align: right;
    }
  }

  .detail-section {
    margin-top: 20px;

    h4 {
      margin-bottom: 15px;
      padding-left: 10px;
      border-left: 4px solid #409EFF;
    }
  }

  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }
}

.starred {
  color: #E6A23C;
}
</style> 