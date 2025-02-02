<template>
  <div class="app-container">
    <h2>耗材库存管理</h2>
    <el-table :data="stockList" style="width: 100%">
      <el-table-column prop="name" label="耗材名称"></el-table-column>
      <el-table-column prop="type" label="耗材类型"></el-table-column>
      <el-table-column prop="count" label="库存数量"></el-table-column>
      <el-table-column prop="unit" label="单位"></el-table-column>
      <el-table-column prop="warning" label="预警值"></el-table-column>
      <el-table-column prop="status" label="状态"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="text" @click="handleHistory(scope.row)">记录</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'ConsumableStock',
  data() {
    return {
      stockList: []
    }
  },
  methods: {
    handleEdit(row) {
      // 编辑操作
    },
    handleHistory(row) {
      // 查看记录
    }
  }
}
</script> 