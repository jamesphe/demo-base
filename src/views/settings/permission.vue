<template>
  <div class="app-container">
    <div class="filter-container">
      <el-button
        class="filter-item"
        type="primary"
        icon="el-icon-plus"
        @click="handleCreate"
      >
        新增权限
      </el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%"
    >
      <el-table-column label="ID" prop="id" align="center" width="80" />
      <el-table-column label="权限名称" prop="name" align="center" />
      <el-table-column label="描述" prop="description" align="center" />
      <el-table-column label="创建时间" align="center" width="180">
        <template slot-scope="{row}">
          <span>{{ row.created_at | parseTime }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="230">
        <template slot-scope="{row}">
          <el-button
            type="primary"
            size="mini"
            @click="handleUpdate(row)"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            size="mini"
            @click="handleDelete(row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.per_page"
      @pagination="getList"
    />

    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="100px"
        style="width: 400px; margin-left:50px;"
      >
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="temp.name" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="temp.description"
            type="textarea"
            :rows="2"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getPermissions, createPermission, updatePermission, deletePermission } from '@/api/permission'
import Pagination from '@/components/Pagination'

export default {
  name: 'PermissionManagement',
  components: { Pagination },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: false,
      listQuery: {
        page: 1,
        per_page: 10
      },
      dialogVisible: false,
      dialogTitle: '',
      temp: {
        id: undefined,
        name: '',
        description: ''
      },
      rules: {
        name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    async getList() {
      try {
        this.listLoading = true
        const { data, meta } = await getPermissions(this.listQuery)
        this.list = data
        this.total = meta.total
      } catch (error) {
        console.error('获取权限列表失败:', error)
        this.$message.error('获取权限列表失败')
      } finally {
        this.listLoading = false
      }
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        name: '',
        description: ''
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogTitle = '新增权限'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row)
      this.dialogTitle = '编辑权限'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    async handleDelete(row) {
      try {
        await this.$confirm('确认删除该权限?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await deletePermission(row.id)
        this.$message.success('删除成功')
        this.getList()
      } catch (error) {
        console.error('删除权限失败:', error)
        this.$message.error('删除权限失败')
      }
    },
    async submitForm() {
      this.$refs['dataForm'].validate(async(valid) => {
        if (valid) {
          try {
            if (this.temp.id) {
              await updatePermission(this.temp.id, this.temp)
              this.$message.success('更新成功')
            } else {
              await createPermission(this.temp)
              this.$message.success('创建成功')
            }
            this.dialogVisible = false
            this.getList()
          } catch (error) {
            console.error('提交表单失败:', error)
            this.$message.error('操作失败')
          }
        }
      })
    }
  }
}
</script>
