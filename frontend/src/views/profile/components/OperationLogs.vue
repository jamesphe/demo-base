<template>
  <div class="operation-logs">
    <el-table
      :data="logs"
      style="width: 100%"
      :default-sort="{ prop: 'date', order: 'descending' }"
    >
      <el-table-column
        prop="date"
        label="操作时间"
        sortable
        width="180"
      />
      <el-table-column
        prop="type"
        label="操作类型"
        width="120"
      />
      <el-table-column
        prop="description"
        label="操作描述"
      />
      <el-table-column
        prop="ip"
        label="IP地址"
        width="140"
      />
    </el-table>

    <div class="pagination-container">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="100"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'OperationLogs',
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      logs: [
        {
          date: '2024-03-31 15:30:00',
          type: '登录',
          description: '用户登录系统',
          ip: '192.168.1.100'
        },
        {
          date: '2024-03-31 14:20:00',
          type: '修改',
          description: '更新个人信息',
          ip: '192.168.1.100'
        },
        {
          date: '2024-03-31 11:15:00',
          type: '查询',
          description: '查看系统配置',
          ip: '192.168.1.100'
        }
      ]
    }
  },
  methods: {
    handlePageChange(page) {
      console.log('当前页:', page)
      // 实现分页逻辑
    }
  }
}
</script>

<style lang="scss" scoped>
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>
