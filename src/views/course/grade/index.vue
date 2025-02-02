<template>
  <div class="app-container">
    <h2>实训成绩评估</h2>
    <el-table :data="gradeList" style="width: 100%">
      <el-table-column prop="course" label="课程" />
      <el-table-column prop="student" label="学生" />
      <el-table-column prop="theory" label="理论成绩" />
      <el-table-column prop="practice" label="实操成绩" />
      <el-table-column prop="report" label="报告成绩" />
      <el-table-column prop="total" label="总评" />
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleEdit(scope.row)">评分</el-button>
          <el-button type="text" @click="handleDetail(scope.row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'CourseGrade',
  data() {
    return {
      gradeList: []
    }
  },
  methods: {
    handleEdit(row) {
      // 评分操作
    },
    handleDetail(row) {
      // 查看详情
    }
  }
}
</script>
