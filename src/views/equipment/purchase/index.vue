<template>
  <div class="app-container">
    <h2>设备采购验收</h2>
    <el-table :data="purchaseList" style="width: 100%">
      <el-table-column prop="name" label="设备名称"></el-table-column>
      <el-table-column prop="supplier" label="供应商"></el-table-column>
      <el-table-column prop="price" label="采购价格"></el-table-column>
      <el-table-column prop="count" label="数量"></el-table-column>
      <el-table-column prop="status" label="验收状态"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleAccept(scope.row)">验收</el-button>
          <el-button type="text" @click="handleView(scope.row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'EquipmentPurchase',
  data() {
    return {
      purchaseList: []
    }
  },
  methods: {
    handleAccept(row) {
      // 验收操作
    },
    handleView(row) {
      // 查看详情
    }
  }
}
</script> 