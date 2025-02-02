<template>
  <div class="app-container">
    <h2>耗材申报审核</h2>
    <el-table :data="applyList" style="width: 100%">
      <el-table-column prop="name" label="耗材名称"></el-table-column>
      <el-table-column prop="type" label="耗材类型"></el-table-column>
      <el-table-column prop="count" label="申请数量"></el-table-column>
      <el-table-column prop="applicant" label="申请人"></el-table-column>
      <el-table-column prop="reason" label="申请理由"></el-table-column>
      <el-table-column prop="status" label="审核状态"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleApprove(scope.row)">审核</el-button>
          <el-button type="text" @click="handleView(scope.row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'ConsumableApply',
  data() {
    return {
      applyList: []
    }
  },
  methods: {
    handleApprove(row) {
      // 审核操作
    },
    handleView(row) {
      // 查看详情
    }
  }
}
</script> 