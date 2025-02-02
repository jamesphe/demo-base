<template>
  <div class="app-container">
    <h2>设备盘点记录</h2>
    <el-table :data="inventoryList" style="width: 100%">
      <el-table-column prop="name" label="设备名称"></el-table-column>
      <el-table-column prop="count" label="盘点数量"></el-table-column>
      <el-table-column prop="date" label="盘点日期"></el-table-column>
      <el-table-column prop="operator" label="盘点人员"></el-table-column>
      <el-table-column prop="status" label="状态"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleView(scope.row)">查看</el-button>
          <el-button type="text" @click="handleExport(scope.row)">导出</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'EquipmentInventory',
  data() {
    return {
      inventoryList: []
    }
  },
  methods: {
    handleView(row) {
      // 查看详情
    },
    handleExport(row) {
      // 导出记录
    }
  }
}
</script> 