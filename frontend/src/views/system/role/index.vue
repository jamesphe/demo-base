<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>角色管理</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="handleAdd">新增角色</el-button>
      </div>

      <el-table :data="roleList" style="width: 100%" border>
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="code" label="角色编码" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="status" label="状态">
          <template slot-scope="{row}">
            <el-tag :type="row.status === '1' ? 'success' : 'info'">
              {{ row.status === '1' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template slot-scope="{row}">
            <el-button type="text" @click="handleEdit(row)">编辑</el-button>
            <el-button type="text" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Role',
  data() {
    return {
      roleList: [
        {
          name: '超级管理员',
          code: 'ADMIN',
          description: '系统管理员',
          status: '1'
        }
      ]
    }
  },
  methods: {
    handleAdd() {
      this.$message('新增角色')
    },
    handleEdit(row) {
      this.$message('编辑角色:' + row.name)
    },
    handleDelete(row) {
      this.$confirm('确认删除该角色?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$message.success('删除成功')
      }).catch(() => {})
    }
  }
}
</script>
