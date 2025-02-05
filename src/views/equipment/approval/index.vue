<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.keyword"
        placeholder="设备名称/申报人"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select
        v-model="listQuery.status"
        placeholder="审核状态"
        style="width: 120px"
        class="filter-item"
        clearable
      >
        <el-option
          v-for="item in statusOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" type="success" @click="handleBatchApprove">
        批量通过
      </el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="approvalList"
      border
      fit
      highlight-current-row
      style="width: 100%;"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="applyCode" label="申请编号" width="120" />
      <el-table-column prop="equipmentName" label="设备名称" min-width="120" />
      <el-table-column prop="model" label="设备型号" width="120" />
      <el-table-column prop="price" label="预计价格" width="120" align="right">
        <template slot-scope="{row}">
          ¥ {{ row.price.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="申请数量" width="100" align="center" />
      <el-table-column prop="applyReason" label="申请理由" min-width="200" show-overflow-tooltip />
      <el-table-column prop="applicant" label="申请人" width="100" />
      <el-table-column prop="applyDate" label="申请日期" width="100" />
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status | statusTextFilter }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="200" fixed="right">
        <template slot-scope="{row}">
          <div style="white-space: nowrap;">
            <el-button 
              v-if="row.status === 'pending'"
              type="success" 
              size="mini" 
              @click="handleApprove(row)"
            >
              通过
            </el-button>
            <el-button 
              v-if="row.status === 'pending'"
              type="danger" 
              size="mini" 
              @click="handleReject(row)"
            >
              拒绝
            </el-button>
            <el-button type="primary" size="mini" @click="handleViewDetails(row)">
              查看
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <!-- 拒绝原因对话框 -->
    <el-dialog title="拒绝原因" :visible.sync="rejectDialogVisible" width="30%">
      <el-form>
        <el-form-item>
          <el-input
            v-model="rejectReason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因"
          />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="rejectDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitReject">确 定</el-button>
      </span>
    </el-dialog>

    <!-- 详情对话框 -->
    <detail-dialog
      :visible.sync="detailDialogVisible"
      :detail="currentDetail"
      @approve="handleApprove"
      @reject="handleReject"
    />
  </div>
</template>

<script>
import { getEquipmentApprovalList, approveEquipment, rejectEquipment, batchApproveEquipment } from '@/api/equipment'
import Pagination from '@/components/Pagination'
import DetailDialog from './components/DetailDialog'

export default {
  name: 'EquipmentApproval',
  components: { Pagination, DetailDialog },
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
  data() {
    return {
      listLoading: false,
      approvalList: [],
      total: 0,
      listQuery: {
        page: 1,
        limit: 10,
        keyword: '',
        status: ''
      },
      statusOptions: [
        { label: '待审核', value: 'pending' },
        { label: '已通过', value: 'approved' },
        { label: '已拒绝', value: 'rejected' }
      ],
      multipleSelection: [],
      rejectDialogVisible: false,
      rejectReason: '',
      currentRow: null,
      detailDialogVisible: false,
      currentDetail: {}
    }
  },
  created() {
    this.getList()
  },
  methods: {
    async getList() {
      this.listLoading = true
      try {
        const { data } = await getEquipmentApprovalList(this.listQuery)
        this.approvalList = data.items
        this.total = data.total
      } catch (error) {
        console.error('Failed to get approval list:', error)
      }
      this.listLoading = false
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleSelectionChange(val) {
      this.multipleSelection = val
    },
    async handleApprove(row) {
      try {
        await this.$confirm('确认通过该设备申请？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await approveEquipment(row.id)
        this.$message({
          type: 'success',
          message: '审核通过成功！'
        })
        this.getList()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to approve:', error)
        }
      }
    },
    handleReject(row) {
      this.currentRow = row
      this.rejectDialogVisible = true
    },
    async submitReject() {
      if (!this.rejectReason.trim()) {
        this.$message({
          message: '请输入拒绝原因',
          type: 'warning'
        })
        return
      }
      try {
        await rejectEquipment({
          id: this.currentRow.id,
          reason: this.rejectReason
        })
        this.$message({
          type: 'success',
          message: '已拒绝该申请'
        })
        this.rejectDialogVisible = false
        this.rejectReason = ''
        this.currentRow = null
        this.getList()
      } catch (error) {
        console.error('Failed to reject:', error)
      }
    },
    async handleBatchApprove() {
      if (this.multipleSelection.length === 0) {
        this.$message({
          message: '请至少选择一条记录',
          type: 'warning'
        })
        return
      }
      try {
        await this.$confirm(`确认批量通过选中的 ${this.multipleSelection.length} 条申请？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        const ids = this.multipleSelection.map(item => item.id)
        await batchApproveEquipment(ids)
        this.$message({
          type: 'success',
          message: '批量审核通过成功！'
        })
        this.getList()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to batch approve:', error)
        }
      }
    },
    handleViewDetails(row) {
      this.currentDetail = { ...row }
      this.detailDialogVisible = true
    }
  }
}
</script>

<style lang="scss" scoped>
.filter-container {
  padding-bottom: 10px;
  .filter-item {
    margin-right: 10px;
  }
}
</style>
