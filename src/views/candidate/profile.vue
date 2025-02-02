<template>
  <div class="app-container">
    <el-card>
      <!-- 搜索栏 -->
      <div class="filter-container">
        <el-input
          v-model="listQuery.name"
          placeholder="候选人姓名"
          style="width: 200px;"
          class="filter-item"
        />
        <el-select
          v-model="listQuery.status"
          placeholder="状态"
          clearable
          style="width: 120px"
          class="filter-item"
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
        <el-button class="filter-item" type="primary" icon="el-icon-plus" @click="handleCreate">
          新增候选人
        </el-button>
      </div>

      <!-- 候选人列表 -->
      <el-table
        :data="list"
        border
        style="width: 100%"
        v-loading="listLoading"
      >
        <el-table-column label="姓名" prop="name" />
        <el-table-column label="联系电话" prop="phone" />
        <el-table-column label="邮箱" prop="email" />
        <el-table-column label="学历" prop="education" />
        <el-table-column label="工作年限" prop="workYears" />
        <el-table-column label="状态" prop="status">
          <template slot-scope="{row}">
            <el-tag :type="row.status | statusFilter">
              {{ row.status | statusLabelFilter }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="230">
          <template slot-scope="{row}">
            <el-button size="mini" @click="handleEdit(row)">编辑</el-button>
            <el-button size="mini" type="success" @click="handleView(row)">查看</el-button>
            <el-button size="mini" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <pagination
        v-show="total>0"
        :total="total"
        :page.sync="listQuery.page"
        :limit.sync="listQuery.limit"
        @pagination="getList"
      />
    </el-card>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination'
import { getCandidateList } from '@/api/candidate'

export default {
  name: 'CandidateProfile',
  components: { Pagination },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: false,
      listQuery: {
        page: 1,
        limit: 10,
        name: undefined,
        status: undefined
      },
      statusOptions: [
        { label: '待处理', value: 'pending' },
        { label: '面试中', value: 'interviewing' },
        { label: '已录用', value: 'hired' },
        { label: '已拒绝', value: 'rejected' }
      ]
    }
  },
  filters: {
    statusFilter(status) {
      const statusMap = {
        pending: 'info',
        interviewing: 'warning',
        hired: 'success',
        rejected: 'danger'
      }
      return statusMap[status]
    },
    statusLabelFilter(status) {
      const statusMap = {
        pending: '待处理',
        interviewing: '面试中',
        hired: '已录用',
        rejected: '已拒绝'
      }
      return statusMap[status]
    }
  },
  created() {
    this.getList()
  },
  methods: {
    async getList() {
      this.listLoading = true
      try {
        const { data } = await getCandidateList(this.listQuery)
        this.list = data.items
        this.total = data.total
      } catch (error) {
        console.error('获取候选人列表失败:', error)
      }
      this.listLoading = false
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleCreate() {
      // TODO: 实现新增候选人功能
    },
    handleEdit(row) {
      // TODO: 实现编辑候选人功能
    },
    handleView(row) {
      // TODO: 实现查看候选人详情功能
    },
    handleDelete(row) {
      // TODO: 实现删除候选人功能
    }
  }
}
</script> 