<template>
  <div class="app-container">
    <h2>设备日常管理</h2>
    <el-table :data="maintainList" style="width: 100%">
      <el-table-column prop="name" label="设备名称" />
      <el-table-column prop="type" label="维护类型" />
      <el-table-column prop="date" label="维护日期" />
      <el-table-column prop="operator" label="维护人员" />
      <el-table-column prop="status" label="状态" />
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
  name: 'EquipmentMaintain',
  data() {
    return {
      maintainList: []
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
