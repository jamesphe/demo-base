<template>
  <div class="app-container">
    <h2>考勤课堂互动</h2>
    <el-table :data="attendanceList" style="width: 100%">
      <el-table-column prop="course" label="课程"></el-table-column>
      <el-table-column prop="student" label="学生"></el-table-column>
      <el-table-column prop="date" label="日期"></el-table-column>
      <el-table-column prop="type" label="考勤方式"></el-table-column>
      <el-table-column prop="status" label="状态"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleSign(scope.row)">签到</el-button>
          <el-button type="text" @click="handleInteract(scope.row)">互动</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'CourseAttendance',
  data() {
    return {
      attendanceList: []
    }
  },
  methods: {
    handleSign(row) {
      // 签到操作
    },
    handleInteract(row) {
      // 互动操作
    }
  }
}
</script> 