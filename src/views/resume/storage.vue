<template>
  <basic-view title="简历存储">
    <div class="storage-container">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="form-inline">
          <el-form-item label="存储位置">
            <el-select v-model="searchForm.location" placeholder="请选择">
              <el-option label="本地存储" value="local" />
              <el-option label="云存储" value="cloud" />
            </el-select>
          </el-form-item>
          <el-form-item label="文件类型">
            <el-select v-model="searchForm.fileType" placeholder="请选择">
              <el-option label="全部" value="" />
              <el-option label="PDF" value="pdf" />
              <el-option label="Word" value="word" />
              <el-option label="图片" value="image" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 存储统计 -->
      <el-row :gutter="20" class="statistics">
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="statistic-item">
              <div class="label">总存储量</div>
              <div class="value">{{ formatSize(statistics.totalSize) }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="statistic-item">
              <div class="label">文件总数</div>
              <div class="value">{{ statistics.totalFiles }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="statistic-item">
              <div class="label">本月新增</div>
              <div class="value">{{ statistics.monthlyNew }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div class="statistic-item">
              <div class="label">存储使用率</div>
              <div class="value">{{ statistics.usageRate }}%</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 文件列表 -->
      <el-table :data="fileList" style="width: 100%" v-loading="loading">
        <el-table-column prop="fileName" label="文件名" />
        <el-table-column prop="fileType" label="类型" width="100">
          <template slot-scope="{row}">
            <el-tag>{{ row.fileType.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120">
          <template slot-scope="{row}">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="location" label="存储位置" width="120">
          <template slot-scope="{row}">
            <el-tag :type="row.location === 'local' ? 'success' : 'primary'">
              {{ row.location === 'local' ? '本地存储' : '云存储' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uploadTime" label="上传时间" width="180">
          <template slot-scope="{row}">
            {{ formatDate(row.uploadTime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template slot-scope="{row}">
            <el-button type="text" @click="handleDownload(row)">下载</el-button>
            <el-button type="text" @click="handleMove(row)">
              {{ row.location === 'local' ? '移至云端' : '移至本地' }}
            </el-button>
            <el-button type="text" class="delete-btn" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="page.current"
          :page-sizes="[10, 20, 30, 50]"
          :page-size="page.size"
          layout="total, sizes, prev, pager, next, jumper"
          :total="page.total"
        />
      </div>
    </div>
  </basic-view>
</template>

<script>
import BasicView from '@/components/BasicView'

export default {
  name: 'ResumeStorage',
  components: { BasicView },
  data() {
    return {
      loading: false,
      searchForm: {
        location: '',
        fileType: ''
      },
      statistics: {
        totalSize: 1024 * 1024 * 1024, // 1GB
        totalFiles: 100,
        monthlyNew: 20,
        usageRate: 75
      },
      fileList: [],
      page: {
        current: 1,
        size: 10,
        total: 0
      }
    }
  },
  created() {
    this.getFileList()
  },
  methods: {
    // 获取文件列表
    async getFileList() {
      this.loading = true
      try {
        // 模拟数据，实际需要调用API
        this.fileList = [
          {
            id: 1,
            fileName: '张三的简历.pdf',
            fileType: 'pdf',
            size: 1024 * 1024, // 1MB
            location: 'local',
            uploadTime: '2024-03-20 10:00:00'
          },
          {
            id: 2,
            fileName: '李四的简历.doc',
            fileType: 'word',
            size: 2 * 1024 * 1024, // 2MB
            location: 'cloud',
            uploadTime: '2024-03-20 11:00:00'
          }
        ]
        this.page.total = 100
      } catch (error) {
        this.$message.error('获取文件列表失败')
      }
      this.loading = false
    },

    // 格式化文件大小
    formatSize(size) {
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let index = 0
      while (size >= 1024 && index < units.length - 1) {
        size /= 1024
        index++
      }
      return size.toFixed(2) + ' ' + units[index]
    },

    // 格式化日期
    formatDate(date) {
      return new Date(date).toLocaleString()
    },

    // 搜索
    handleSearch() {
      this.page.current = 1
      this.getFileList()
    },

    // 重置搜索
    resetSearch() {
      this.searchForm = {
        location: '',
        fileType: ''
      }
      this.handleSearch()
    },

    // 下载文件
    handleDownload(row) {
      this.$message.success(`开始下载: ${row.fileName}`)
    },

    // 移动存储位置
    async handleMove(row) {
      try {
        await this.$confirm(`确认将文件移至${row.location === 'local' ? '云端' : '本地'}存储?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        row.location = row.location === 'local' ? 'cloud' : 'local'
        this.$message.success('移动成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('移动失败')
        }
      }
    },

    // 删除文件
    async handleDelete(row) {
      try {
        await this.$confirm('确认删除该文件?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const index = this.fileList.indexOf(row)
        this.fileList.splice(index, 1)
        this.$message.success('删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
        }
      }
    },

    // 分页大小改变
    handleSizeChange(val) {
      this.page.size = val
      this.getFileList()
    },

    // 当前页改变
    handleCurrentChange(val) {
      this.page.current = val
      this.getFileList()
    }
  }
}
</script>

<style lang="scss" scoped>
.storage-container {
  padding: 20px;

  .search-bar {
    margin-bottom: 20px;
  }

  .statistics {
    margin-bottom: 20px;

    .statistic-item {
      text-align: center;
      
      .label {
        color: #909399;
        font-size: 14px;
        margin-bottom: 10px;
      }
      
      .value {
        color: #303133;
        font-size: 24px;
        font-weight: bold;
      }
    }
  }

  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }
}

.delete-btn {
  color: #F56C6C;
}
</style> 