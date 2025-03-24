<template>
  <el-card class="tenant-list-card">
    <div slot="header" class="clearfix">
      <span>租户列表</span>
      <el-button style="float: right; padding: 3px 0" type="text" @click="refreshList">刷新</el-button>
    </div>
    <el-table
      :data="tenants"
      style="width: 100%"
      :header-cell-style="{background:'#f5f7fa',color:'#606266'}"
      v-loading="loading">
      <el-table-column
        prop="name"
        label="租户名称"
        width="180">
      </el-table-column>
      <el-table-column
        prop="status"
        label="状态">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
            {{ scope.row.status === 'active' ? '活跃' : '非活跃' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="createdAt"
        label="创建时间">
      </el-table-column>
      <el-table-column
        label="操作"
        width="120">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            @click="handleDetail(scope.row)">详情</el-button>
          <el-button
            size="mini"
            type="text"
            @click="handleManage(scope.row)">管理</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script>
export default {
  name: 'TenantList',
  data() {
    return {
      loading: false,
      tenants: [
        {
          id: 1,
          name: '示例租户1',
          status: 'active',
          createdAt: '2023-01-15'
        },
        {
          id: 2,
          name: '示例租户2',
          status: 'active',
          createdAt: '2023-02-20'
        },
        {
          id: 3,
          name: '示例租户3',
          status: 'inactive',
          createdAt: '2023-03-10'
        }
      ]
    }
  },
  methods: {
    refreshList() {
      this.loading = true
      // 模拟API请求
      setTimeout(() => {
        this.loading = false
      }, 800)
    },
    handleDetail(row) {
      this.$message.info(`查看租户详情：${row.name}`)
    },
    handleManage(row) {
      this.$message.info(`管理租户：${row.name}`)
    }
  }
}
</script>

<style scoped>
.tenant-list-card {
  margin-bottom: 20px;
}
</style> 