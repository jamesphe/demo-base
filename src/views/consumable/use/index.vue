<template>
  <div class="app-container">
    <h2>耗材领用统计</h2>
    <el-table :data="useList" style="width: 100%">
      <el-table-column prop="name" label="耗材名称" />
      <el-table-column prop="department" label="领用部门" />
      <el-table-column prop="count" label="领用数量" />
      <el-table-column prop="applicant" label="领用人" />
      <el-table-column prop="date" label="领用日期" />
      <el-table-column prop="purpose" label="用途" />
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleView(scope.row)">查看</el-button>
          <el-button type="text" @click="handleExport(scope.row)">导出</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'ConsumableUse',
  data() {
    return {
      useList: []
    }
  },
  methods: {
    handleView(row) {
      // 查看详情
    },
    handleExport(row) {
      // 导出记录
    }
  }
}
</script>
