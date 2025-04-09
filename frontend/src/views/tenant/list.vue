<template>
  <div class="app-container">
    <el-card class="box-card">
      <div class="filter-container">
        <el-input
          v-model="listQuery.keyword"
          placeholder="请输入租户名称"
          style="width: 200px;"
          class="filter-item"
          @keyup.enter.native="handleFilter"
        />
        <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
          搜索
        </el-button>
        <el-button class="filter-item" type="primary" icon="el-icon-plus" @click="handleCreate">
          添加
        </el-button>
      </div>

      <el-table
        v-loading="listLoading"
        :data="list"
        border
        style="width: 100%"
      >
        <el-table-column
          prop="tenantName"
          label="租户名称"
          align="center"
        />
        <el-table-column
          prop="contactPerson"
          label="联系人"
          align="center"
        />
        <el-table-column
          prop="contactPhone"
          label="联系电话"
          align="center"
        />
        <el-table-column
          prop="status"
          label="状态"
          align="center"
        >
          <template slot-scope="{row}">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          align="center"
          width="230"
        >
          <template slot-scope="{row}">
            <el-button type="primary" size="mini" @click="handleUpdate(row)">
              编辑
            </el-button>
            <el-button :type="row.status === 1 ? 'danger' : 'success'" size="mini" @click="handleStatusChange(row)">
              {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
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
    </el-card>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination'

export default {
  name: 'TenantList',
  components: {
    Pagination
  },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: false,
      listQuery: {
        page: 1,
        limit: 10,
        keyword: ''
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      // 这里添加获取租户列表的API调用
      // fetchTenantList(this.listQuery).then(response => {
      //   this.list = response.data.items
      //   this.total = response.data.total
      //   this.listLoading = false
      // })
      setTimeout(() => {
        this.listLoading = false
        // 模拟数据
        this.list = [
          {
            tenantName: '测试租户',
            contactPerson: '张三',
            contactPhone: '13800138000',
            status: 1
          }
        ]
        this.total = 1
      }, 1000)
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleCreate() {
      // 实现添加租户的逻辑
    },
    handleUpdate(row) {
      // 实现编辑租户的逻辑
    },
    handleStatusChange(row) {
      // 实现状态变更的逻辑
    }
  }
}
</script>
