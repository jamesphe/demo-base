<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>菜单管理</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="handleAdd">新增菜单</el-button>
      </div>

      <el-table
        :data="menuList"
        style="width: 100%;margin-bottom: 20px;"
        row-key="id"
        border
        default-expand-all
        :tree-props="{children: 'children', hasChildren: 'hasChildren'}"
      >
        <el-table-column prop="title" label="菜单名称" />
        <el-table-column prop="icon" label="图标" align="center" width="80">
          <template slot-scope="{row}">
            <svg-icon :icon-class="row.icon" />
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template slot-scope="{row}">
            <el-tag :type="row.status === '1' ? 'success' : 'info'">
              {{ row.status === '1' ? '显示' : '隐藏' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template slot-scope="{row}">
            <el-button type="text" @click="handleAdd(row)">新增</el-button>
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
  name: 'Menu',
  data() {
    return {
      menuList: [
        {
          id: 1,
          title: '系统管理',
          icon: 'system',
          sort: 1,
          status: '1',
          children: [
            {
              id: 2,
              title: '用户管理',
              icon: 'user',
              sort: 1,
              status: '1'
            },
            {
              id: 3,
              title: '角色管理',
              icon: 'peoples',
              sort: 2,
              status: '1'
            },
            {
              id: 4,
              title: '菜单管理',
              icon: 'tree',
              sort: 3,
              status: '1'
            }
          ]
        }
      ]
    }
  },
  methods: {
    handleAdd(row) {
      this.$message('新增菜单')
    },
    handleEdit(row) {
      this.$message('编辑菜单:' + row.title)
    },
    handleDelete(row) {
      this.$confirm('确认删除该菜单?', '提示', {
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
