<template>
  <el-card class="tenant-overview">
    <div slot="header" class="clearfix">
      <span>租户概览</span>
      <el-button style="float: right; padding: 3px 0" type="text" @click="refreshData">
        刷新
      </el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="tenantList"
      style="width: 100%"
      :header-cell-style="{background:'#f5f7fa'}"
    >
      <el-table-column
        prop="name"
        label="租户名称"
      />

      <el-table-column
        prop="type"
        label="类型"
        width="100"
      >
        <template slot-scope="{row}">
          <el-tag :type="row.type === 'enterprise' ? 'success' : 'warning'">
            {{ row.type === 'enterprise' ? '企业版' : '试用版' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column
        prop="userCount"
        label="用户数"
        width="100"
      />

      <el-table-column
        prop="status"
        label="状态"
        width="100"
      >
        <template slot-scope="{row}">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column
        label="操作"
        width="150"
        align="center"
      >
        <template slot-scope="{row}">
          <el-button
            size="mini"
            type="text"
            @click="handleManage(row)"
          >
            管理
          </el-button>
          <el-button
            size="mini"
            :class="row.status === 'active' ? 'text-danger' : 'text-success'"
            type="text"
            @click="handleStatusChange(row)"
          >
            {{ row.status === 'active' ? '停用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script>
export default {
  name: 'TenantOverview',
  data() {
    return {
      loading: false,
      tenantList: [
        {
          name: '示例企业科技有限公司',
          type: 'enterprise',
          userCount: 56,
          status: 'active'
        },
        {
          name: '测试科技有限公司',
          type: 'trial',
          userCount: 12,
          status: 'active'
        }
      ]
    }
  },
  methods: {
    refreshData() {
      this.loading = true
      // TODO: 调用API获取最新数据
      setTimeout(() => {
        this.loading = false
      }, 800)
    },
    handleManage(tenant) {
      this.$router.push(`/tenant/detail/${tenant.id}`)
    },
    handleStatusChange(tenant) {
      // TODO: 调用API修改租户状态
    }
  }
}
</script>

<style lang="scss" scoped>
.text-danger {
  color: #F56C6C;
}
.text-success {
  color: #67C23A;
}
</style>
