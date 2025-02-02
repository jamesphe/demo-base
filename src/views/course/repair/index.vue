<template>
  <div class="app-container">
    <h2>设备损坏维修</h2>
    <el-table :data="repairList" style="width: 100%">
      <el-table-column prop="equipment" label="设备名称"></el-table-column>
      <el-table-column prop="type" label="故障类型"></el-table-column>
      <el-table-column prop="description" label="故障描述"></el-table-column>
      <el-table-column prop="reporter" label="报修人"></el-table-column>
      <el-table-column prop="date" label="报修时间"></el-table-column>
      <el-table-column prop="status" label="维修状态"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleProcess(scope.row)">处理</el-button>
          <el-button type="text" @click="handleView(scope.row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'CourseRepair',
  data() {
    return {
      repairList: []
    }
  },
  methods: {
    handleProcess(row) {
      // 处理维修
    },
    handleView(row) {
      // 查看详情
    }
  }
}
</script> 