<template>
  <div class="app-container">
    <h2>耗材采购入库</h2>
    <el-table :data="purchaseList" style="width: 100%">
      <el-table-column prop="name" label="耗材名称"></el-table-column>
      <el-table-column prop="supplier" label="供应商"></el-table-column>
      <el-table-column prop="price" label="采购价格"></el-table-column>
      <el-table-column prop="count" label="数量"></el-table-column>
      <el-table-column prop="batch" label="批次号"></el-table-column>
      <el-table-column prop="status" label="入库状态"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button type="text" @click="handleStorage(scope.row)">入库</el-button>
          <el-button type="text" @click="handleView(scope.row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'ConsumablePurchase',
  data() {
    return {
      purchaseList: []
    }
  },
  methods: {
    handleStorage(row) {
      // 入库操作
    },
    handleView(row) {
      // 查看详情
    }
  }
}
</script> 