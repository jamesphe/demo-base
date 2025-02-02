<template>
  <div class="app-container">
    <h2>课程计划课表</h2>
    <el-table :data="planList" style="width: 100%">
      <el-table-column prop="name" label="课程名称"></el-table-column>
      <el-table-column prop="teacher" label="授课教师"></el-table-column>
      <el-table-column prop="room" label="实训室"></el-table-column>
      <el-table-column prop="time" label="上课时间"></el-table-column>
      <el-table-column prop="class" label="班级"></el-table-column>
      <el-table-column prop="status" label="状态"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="text" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'CoursePlan',
  data() {
    return {
      planList: []
    }
  },
  methods: {
    handleEdit(row) {
      // 编辑操作
    },
    handleDelete(row) {
      // 删除操作
    }
  }
}
</script> 