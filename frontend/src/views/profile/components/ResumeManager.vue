<template>
  <div class="resume-manager">
    <div class="resume-list">
      <el-table :data="resumes" style="width: 100%">
        <el-table-column prop="name" label="简历名称" />
        <el-table-column prop="updateTime" label="更新时间" />
        <el-table-column prop="status" label="状态" />
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button type="text" @click="previewResume(scope.row)">预览</el-button>
            <el-button type="text" @click="editResume(scope.row)">编辑</el-button>
            <el-button type="text" @click="downloadResume(scope.row)">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResumeManager',
  data() {
    return {
      resumes: []
    }
  },
  methods: {
    previewResume(resume) {
      console.log('预览简历:', resume)
    },
    editResume(resume) {
      console.log('编辑简历:', resume)
    },
    downloadResume(resume) {
      console.log('下载简历:', resume)
    }
  }
}
</script>
