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

      <!-- 添加分页组件 -->
      <div class="pagination-container">
        <el-pagination
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="listQuery.page"
          :page-sizes="[10, 20, 30, 50]"
          :page-size="listQuery.limit"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        />
      </div>

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
      currentResult: {},
      listQuery: {
        page: 1,
        limit: 10
      },
      total: 0
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
        console.log('开始获取解析列表...')
        const res = await getParseList({
          page: this.listQuery.page,
          limit: this.listQuery.limit
        })
        console.log('获取解析列表响应:', res)
        
        // 确保 data 和 items 存在
        if (!res.data || !res.data.items) {
          throw new Error('返回数据格式错误')
        }
        
        this.parseList = res.data.items.map(item => ({
          id: item.id,
          fileName: item.file_name,
          fileUrl: item.file_url,
          uploadTime: item.created_at,
          parseStatus: item.processing_status || 'pending',
          parsedData: item.parsed_data
        }))

        // 更新总数
        this.total = res.data.total || 0

      } catch (error) {
        console.error('获取解析列表失败:', {
          message: error.message,
          config: error.config,
          response: error.response?.data
        })
        this.$message.error(error.response?.data?.detail || error.message || '获取列表失败')
      } finally {
        this.loading = false
        console.log('获取解析列表完成')
      }
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
        const parsedData = data.parsed_data || {}
        
        this.currentResult = {
          name: parsedData.name || '',
          gender: parsedData.gender || '',
          age: parsedData.age || '',
          phone: parsedData.phone || '',
          email: parsedData.email || '',
          education: parsedData.highest_education || '',
          workExperience: parsedData.work_experience || [],
          educationExperience: parsedData.education || []
        }
      } catch (error) {
        console.error('获取解析结果失败:', error)
        this.$message.error(error.message || '获取解析结果失败')
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
        
        // 创建一个新对象来追踪状态
        const updatedRow = { ...row }
        updatedRow.parseStatus = 'parsing'
        Object.assign(row, updatedRow)
        
        await parseResume(row.fileUrl)
        
        updatedRow.parseStatus = 'success'
        Object.assign(row, updatedRow)
        
        this.$message.success('解析成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('解析失败')
          const updatedRow = { ...row }
          updatedRow.parseStatus = 'failed'
          Object.assign(row, updatedRow)
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
    },

    // 添加处理页码改变的方法
    handleCurrentChange(page) {
      this.listQuery.page = page
      this.getParseList()
    },

    // 添加处理每页条数改变的方法
    handleSizeChange(limit) {
      this.listQuery.limit = limit
      this.listQuery.page = 1
      this.getParseList()
    }
  }
}
</script>

<style lang="scss" scoped>
.parse-container {
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
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