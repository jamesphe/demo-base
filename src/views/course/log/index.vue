<template>
  <div class="app-container">
    <h2>实训日志管理</h2>
    <el-table :data="logList" style="width: 100%">
      <el-table-column prop="course" label="课程"></el-table-column>
      <el-table-column prop="teacher" label="教师"></el-table-column>
      <el-table-column prop="date" label="日期"></el-table-column>
      <el-table-column prop="content" label="内容"></el-table-column>
      <el-table-column prop="problem" label="问题"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="text" @click="handleView(scope.row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'CourseLog',
  data() {
    return {
      logList: []
    }
  },
  methods: {
    handleEdit(row) {
      // 编辑操作
    },
    handleView(row) {
      // 查看详情
    }
  }
}
</script> 