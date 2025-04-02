<template>
  <div class="app-container">
    <div class="filter-container">
      <el-button
        class="filter-item"
        type="primary"
        icon="el-icon-plus"
        @click="handleCreate"
      >
        新建角色
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
      <el-table-column label="角色名称" prop="name" align="center" />
      <el-table-column label="描述" prop="description" align="center" />
      <el-table-column label="创建时间" align="center" width="180">
        <template #default="{ row }">
          <span>{{ row.created_at | parseTime }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="250">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="mini"
            @click="handleUpdate(row)"
          >
            编辑
          </el-button>
          <el-button
            type="success"
            size="mini"
            @click="handlePermission(row)"
          >
            权限
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
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.per_page"
      @pagination="getList"
    />

    <!-- 角色表单对话框 -->
    <el-dialog
      :title="dialogTitle"
      :visible.sync="dialogVisible"
      width="500px"
    >
      <el-form
        ref="dataForm"
        :model="temp"
        :rules="rules"
        label-position="left"
        label-width="80px"
        style="margin-left: 50px; margin-right: 50px"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="temp.name" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="temp.description"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确认</el-button>
      </div>
    </el-dialog>

    <!-- 权限设置对话框 -->
    <el-dialog
      title="设置权限"
      :visible.sync="permissionDialogVisible"
      width="800px"
      class="permission-dialog"
    >
      <div class="permission-header">
        <div class="role-info">
          <span class="label">角色名称:</span>
          <span class="value">{{ currentRole ? currentRole.name : '-' }}</span>
        </div>
        <div class="role-info">
          <span class="label">角色描述:</span>
          <span class="value">{{ currentRole && currentRole.description ? currentRole.description : '-' }}</span>
        </div>
      </div>

      <el-transfer
        v-model="selectedPermissions"
        :data="allPermissions"
        :titles="['可选权限', '已选权限']"
        :props="{
          key: 'id',
          label: 'name'
        }"
        :button-texts="['移除权限', '添加权限']"
        filterable
        filter-placeholder="请输入权限名称"
      >
        <template #left-footer>
          <div class="transfer-footer">
            <span class="count">共 {{ allPermissions.length }} 项</span>
          </div>
        </template>
        <template #right-footer>
          <div class="transfer-footer">
            <span class="count">已选 {{ selectedPermissions.length }} 项</span>
          </div>
        </template>
      </el-transfer>

      <div slot="footer" class="dialog-footer">
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="updatePermLoading"
          @click="updatePermissions"
        >确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getRoles, createRole, updateRole, deleteRole, updateRolePermissions } from '@/api/role'
import { getPermissions, getRolePermissions } from '@/api/permission'
import Pagination from '@/components/Pagination'
import { parseTime } from '@/utils'

export default {
  name: 'Role',
  components: { Pagination },
  filters: {
    parseTime
  },
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
        name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
      },
      permissionDialogVisible: false,
      currentRole: null,
      allPermissions: [], // 所有权限列表
      selectedPermissions: [], // 已选择的权限ID列表
      updatePermLoading: false
    }
  },
  created() {
    this.getList()
  },
  methods: {
    async getList() {
      this.listLoading = true
      try {
        const response = await getRoles(this.listQuery)
        this.list = response.data
        this.total = response.meta.total
      } catch (error) {
        console.error('获取角色列表失败:', error)
      }
      this.listLoading = false
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
      this.dialogTitle = '新建角色'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row)
      this.dialogTitle = '编辑角色'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    async submitForm() {
      this.$refs.dataForm.validate(async valid => {
        if (valid) {
          try {
            if (this.temp.id) {
              await updateRole(this.temp.id, this.temp)
            } else {
              await createRole(this.temp)
            }
            this.dialogVisible = false
            this.$message({
              type: 'success',
              message: '操作成功!'
            })
            this.getList()
          } catch (error) {
            console.error('提交表单失败:', error)
          }
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该角色?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async() => {
        try {
          await deleteRole(row.id)
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
          this.getList()
        } catch (error) {
          console.error('删除角色失败:', error)
        }
      })
    },
    async handlePermission(row) {
      this.currentRole = row
      this.permissionDialogVisible = true
      this.selectedPermissions = []
      try {
        // 获取所有权限列表
        const allPermsResponse = await getPermissions()
        this.allPermissions = (allPermsResponse.data || []).map(item => ({
          id: item.id,
          name: `${item.name}(${item.description})`,
          description: item.description
        }))

        // 获取当前角色的权限
        const rolePermsResponse = await getRolePermissions(row.id)
        this.selectedPermissions = (rolePermsResponse || []).map(item => item.id)
      } catch (error) {
        console.error('获取权限数据失败:', error)
        this.$message({
          type: 'error',
          message: '获取权限数据失败'
        })
      }
    },
    async updatePermissions() {
      if (!this.currentRole) return
      try {
        this.updatePermLoading = true
        await updateRolePermissions(this.currentRole.id, this.selectedPermissions)
        this.$message({
          type: 'success',
          message: '权限更新成功!'
        })
        this.permissionDialogVisible = false
        // 刷新角色列表
        this.getList()
      } catch (error) {
        console.error('更新权限失败:', error)
        this.$message({
          type: 'error',
          message: '更新权限失败'
        })
      } finally {
        this.updatePermLoading = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.el-transfer {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.permission-dialog {
  ::v-deep .el-dialog__body {
    padding: 20px;
  }

  .permission-header {
    margin-bottom: 20px;
    padding: 15px 20px;
    background-color: #f5f7fa;
    border-radius: 4px;

    .role-info {
      line-height: 24px;

      .label {
        display: inline-block;
        width: 80px;
        color: #606266;
      }

      .value {
        color: #303133;
        font-weight: 500;
      }
    }
  }

  .el-transfer {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 10px 0;

    ::v-deep {
      .el-transfer-panel {
        width: 300px;

        &__header {
          background: #f5f7fa;
        }

        .el-transfer-panel__filter {
          margin: 15px;

          .el-input__inner {
            height: 32px;
          }
        }

        .el-checkbox-group {
          padding: 6px 0;
        }
      }

      .el-transfer__buttons {
        padding: 0 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 12px;

        .el-button {
          display: block;
          width: 100px;
          padding: 8px 0;
          font-size: 13px;
          border-radius: 4px;
          position: relative;
          transition: all 0.3s;

          &:first-child {
            background-color: #f56c6c;
            border-color: #f56c6c;
            color: #fff;

            &:hover {
              background-color: #f78989;
              border-color: #f78989;
            }

            i {
              transform: rotate(0deg);
            }
          }

          &:last-child {
            background-color: #409eff;
            border-color: #409eff;
            color: #fff;

            &:hover {
              background-color: #66b1ff;
              border-color: #66b1ff;
            }
          }

          &[disabled] {
            background-color: #f5f7fa;
            border-color: #e4e7ed;
            color: #c0c4cc;
            cursor: not-allowed;

            &:hover {
              background-color: #f5f7fa;
              border-color: #e4e7ed;
            }
          }

          i {
            font-size: 14px;
            margin-right: 4px;
          }
        }
      }
    }
  }

  .transfer-footer {
    padding: 10px 15px;
    background: #f5f7fa;

    .count {
      color: #606266;
      font-size: 13px;
    }
  }
}
</style>
