<template>
  <div class="app-container">
    <h2>课程设备统计</h2>
    <el-table :data="statisticsList" style="width: 100%">
      <el-table-column prop="course" label="课程名称"></el-table-column>
      <el-table-column prop="equipment" label="设备名称"></el-table-column>
      <el-table-column prop="useCount" label="使用次数"></el-table-column>
      <el-table-column prop="useTime" label="使用时长"></el-table-column>
      <el-table-column prop="faultCount" label="故障次数"></el-table-column>
      <el-table-column prop="department" label="使用院系"></el-table-column>
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
  name: 'CourseStatistics',
  data() {
    return {
      statisticsList: []
    }
  },
  methods: {
    handleView(row) {
      // 查看详情
    },
    handleExport(row) {
      // 导出数据
    }
  }
}
</script> 