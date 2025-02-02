<template>
  <basic-view title="简历解析">
    <div class="parse-container">
      <!-- 解析列表 -->
      <el-table :data="parseList" style="width: 100%" v-loading="loading">
        <el-table-column prop="fileName" label="文件名" width="200" />
        <el-table-column prop="uploadTime" label="上传时间" width="180">
          <template slot-scope="{row}">
            {{ formatDate(row.uploadTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="parseStatus" label="解析状态" width="100">
          <template slot-scope="{row}">
            <el-tag :type="getStatusType(row.parseStatus)">
              {{ getStatusText(row.parseStatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="解析结果">
          <template slot-scope="{row}">
            <el-button 
              type="text"
              @click="showParseResult(row)"
              :disabled="row.parseStatus !== 'success'"
            >
              查看结果
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template slot-scope="{row}">
            <el-button 
              type="text"
              @click="handleParse(row)"
              :disabled="row.parseStatus === 'parsing'"
            >
              {{ row.parseStatus === 'failed' ? '重新解析' : '解析' }}
            </el-button>
            <el-button 
              type="text"
              class="delete-btn"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 解析结果对话框 -->
      <el-dialog
        title="解析结果"
        :visible.sync="resultVisible"
        width="60%"
      >
        <div v-loading="resultLoading">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="姓名">
              {{ currentResult.name }}
            </el-descriptions-item>
            <el-descriptions-item label="性别">
              {{ currentResult.gender }}
            </el-descriptions-item>
            <el-descriptions-item label="年龄">
              {{ currentResult.age }}
            </el-descriptions-item>
            <el-descriptions-item label="电话">
              {{ currentResult.phone }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ currentResult.email }}
            </el-descriptions-item>
            <el-descriptions-item label="最高学历">
              {{ currentResult.education }}
            </el-descriptions-item>
          </el-descriptions>

          <div class="section-title">工作经历</div>
          <el-timeline>
            <el-timeline-item
              v-for="(work, index) in currentResult.workExperience"
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

          <div class="section-title">教育经历</div>
          <el-timeline>
            <el-timeline-item
              v-for="(edu, index) in currentResult.education"
              :key="index"
              :timestamp="edu.period"
              placement="top"
            >
              <el-card>
                <h4>{{ edu.school }} - {{ edu.major }}</h4>
                <p>{{ edu.degree }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-dialog>
    </div>
  </basic-view>
</template>

<script>
import BasicView from '@/components/BasicView'
import { getParseList, parseResume, getParseResult, deleteParseRecord } from '@/api/resume'

export default {
  name: 'ResumeParse',
  components: { BasicView },
  data() {
    return {
      loading: false,
      parseList: [],
      resultVisible: false,
      resultLoading: false,
      currentResult: {}
    }
  },
  created() {
    this.getParseList()
  },
  methods: {
    // 获取解析列表
    async getParseList() {
      this.loading = true
      try {
        const { data } = await getParseList()
        this.parseList = data.items
      } catch (error) {
        this.$message.error('获取列表失败')
      }
      this.loading = false
    },

    // 格式化日期
    formatDate(date) {
      return new Date(date).toLocaleString()
    },

    // 获取状态类型
    getStatusType(status) {
      const types = {
        success: 'success',
        parsing: 'warning',
        failed: 'danger',
        pending: 'info'
      }
      return types[status] || 'info'
    },

    // 获取状态文本
    getStatusText(status) {
      const texts = {
        success: '解析成功',
        parsing: '解析中',
        failed: '解析失败',
        pending: '待解析'
      }
      return texts[status] || '未知状态'
    },

    // 显示解析结果
    async showParseResult(row) {
      this.resultVisible = true
      this.resultLoading = true
      try {
        const { data } = await getParseResult(row.id)
        this.currentResult = data
      } catch (error) {
        this.$message.error('获取解析结果失败')
      }
      this.resultLoading = false
    },

    // 解析简历
    async handleParse(row) {
      try {
        await this.$confirm('确认解析该简历?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        row.parseStatus = 'parsing'
        await parseResume(row.id)
        row.parseStatus = 'success'
        this.$message.success('解析成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('解析失败')
          row.parseStatus = 'failed'
        }
      }
    },

    // 删除简历
    async handleDelete(row) {
      try {
        await this.$confirm('确认删除该简历?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await deleteParseRecord(row.id)
        const index = this.parseList.indexOf(row)
        this.parseList.splice(index, 1)
        this.$message.success('删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.parse-container {
  padding: 20px;
}

.section-title {
  margin: 20px 0;
  padding-left: 10px;
  font-size: 16px;
  font-weight: 500;
  border-left: 4px solid #409EFF;
}

.delete-btn {
  color: #F56C6C;
}
</style> 