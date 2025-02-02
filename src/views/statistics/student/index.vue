<template>
  <div class="app-container">
    <h2>学生成绩统计</h2>
    <el-table :data="statisticsList" style="width: 100%">
      <el-table-column prop="student" label="学生姓名" />
      <el-table-column prop="class" label="班级" />
      <el-table-column prop="courseCount" label="课程数" />
      <el-table-column prop="avgScore" label="平均分" />
      <el-table-column prop="attendance" label="出勤率" />
      <el-table-column prop="ranking" label="排名" />
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleDetail(scope.row)">详情</el-button>
          <el-button type="text" @click="handleExport(scope.row)">导出</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'StudentStatistics',
  data() {
    return {
      statisticsList: []
    }
  },
  methods: {
    handleDetail(row) {
      // 查看详情
    },
    handleExport(row) {
      // 导出数据
    }
  }
}
</script>
