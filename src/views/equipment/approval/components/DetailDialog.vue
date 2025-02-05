<template>
  <el-dialog
    title="申请详情"
    :visible.sync="visible"
    width="50%"
    :close-on-click-modal="false"
  >
    <el-descriptions :column="2" border>
      <el-descriptions-item label="申请编号">{{ detail.applyCode }}</el-descriptions-item>
      <el-descriptions-item label="申请日期">{{ detail.applyDate }}</el-descriptions-item>
      <el-descriptions-item label="设备名称">{{ detail.equipmentName }}</el-descriptions-item>
      <el-descriptions-item label="设备型号">{{ detail.model }}</el-descriptions-item>
      <el-descriptions-item label="预计价格">¥ {{ detail.price ? detail.price.toFixed(2) : '0.00' }}</el-descriptions-item>
      <el-descriptions-item label="申请数量">{{ detail.quantity }}</el-descriptions-item>
      <el-descriptions-item label="申请人">{{ detail.applicant }}</el-descriptions-item>
      <el-descriptions-item label="审核状态">
        <el-tag :type="detail.status | statusFilter">{{ detail.status | statusTextFilter }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="申请理由" :span="2">{{ detail.applyReason }}</el-descriptions-item>
      <el-descriptions-item v-if="detail.status === 'rejected'" label="拒绝原因" :span="2">
        {{ detail.rejectReason }}
      </el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ detail.createTime }}</el-descriptions-item>
      <el-descriptions-item label="更新时间">{{ detail.updateTime }}</el-descriptions-item>
    </el-descriptions>
    <div slot="footer" class="dialog-footer">
      <el-button @click="handleClose">关 闭</el-button>
      <template v-if="detail.status === 'pending'">
        <el-button type="success" @click="$emit('approve', detail)">通 过</el-button>
        <el-button type="danger" @click="$emit('reject', detail)">拒 绝</el-button>
      </template>
    </div>
  </el-dialog>
</template>

<script>
import { ElDescriptions, ElDescriptionsItem } from 'element-ui';

export default {
  name: 'DetailDialog',
  components: { ElDescriptions, ElDescriptionsItem },
  filters: {
    statusFilter(status) {
      const statusMap = {
        pending: 'warning',
        approved: 'success',
        rejected: 'danger'
      }
      return statusMap[status]
    },
    statusTextFilter(status) {
      const statusMap = {
        pending: '待审核',
        approved: '已通过',
        rejected: '已拒绝'
      }
      return statusMap[status]
    }
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    detail: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    handleClose() {
      this.$emit('update:visible', false)
    }
  }
}
</script>

<style lang="scss" scoped>
.el-descriptions {
  margin: 20px 0;
}
</style>
