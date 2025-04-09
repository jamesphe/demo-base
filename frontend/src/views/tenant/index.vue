<template>
  <div class="app-container">
    <!-- 顶部工具栏 -->
    <div class="filter-container">
      <el-button
        class="filter-item"
        type="primary"
        icon="el-icon-plus"
        size="medium"
        @click="handleCreate"
      >
        添加租户
      </el-button>
    </div>

    <!-- 表格区域 -->
    <el-card class="box-card" shadow="hover">
      <el-table
        v-loading="listLoading"
        :data="list"
        border
        fit
        highlight-current-row
        style="width: 100%"
      >
        <el-table-column label="ID" prop="id" align="center" width="80" />
        <el-table-column label="租户名称" prop="tenantName" align="center" min-width="180">
          <template slot-scope="{row}">
            <span class="link-type">{{ row.tenantName }}</span>
          </template>
        </el-table-column>
        <el-table-column label="联系人" prop="contactPerson" align="center" min-width="150" />
        <el-table-column label="联系电话" prop="phone" align="center" min-width="150" />
        <el-table-column label="邮箱" prop="email" align="center" min-width="180" />
        <el-table-column label="状态" prop="status" align="center" width="120">
          <template slot-scope="{row}">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="medium">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="createdAt" align="center" width="180">
          <template slot-scope="{row}">
            <span>{{ parseTime(row.createdAt) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="280" class-name="small-padding fixed-width">
          <template slot-scope="{row}">
            <el-button type="primary" size="small" icon="el-icon-edit" @click="handleUpdate(row)">
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              icon="el-icon-delete"
              class="margin-left"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <pagination
          v-show="total>0"
          :total="total"
          :page.sync="listQuery.page"
          :limit.sync="listQuery.limit"
          @pagination="getList"
        />
      </div>
    </el-card>

    <!-- 弹窗表单 -->
    <el-dialog
      :title="textMap[dialogStatus]"
      :visible.sync="dialogFormVisible"
      width="700px"
      :close-on-click-modal="false"
      custom-class="tenant-dialog"
      @close="handleDialogClose"
    >
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="right"
        label-width="120px"
        class="form-container"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="租户名称" prop="tenantName">
              <el-input
                v-model="temp.tenantName"
                placeholder="请输入租户名称"
                :maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select
                v-model="temp.status"
                class="filter-item"
                placeholder="请选择状态"
                style="width: 100%"
              >
                <el-option key="active" label="启用" value="active">
                  <i class="el-icon-check status-icon" style="color: #67C23A" />
                  <span>启用</span>
                </el-option>
                <el-option key="inactive" label="禁用" value="inactive">
                  <i class="el-icon-close status-icon" style="color: #909399" />
                  <span>禁用</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contactPerson">
              <el-input
                v-model="temp.contactPerson"
                placeholder="请输入联系人"
                :maxlength="20"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input
                v-model="temp.phone"
                placeholder="请输入联系电话"
                :maxlength="20"
              >
                <i slot="prefix" class="el-icon-phone" />
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="temp.email"
                placeholder="请输入邮箱"
                :maxlength="50"
              >
                <i slot="prefix" class="el-icon-message" />
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="外部ID" prop="externalId">
              <el-input
                v-model="temp.externalId"
                placeholder="请输入外部ID"
                :maxlength="30"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="地址" prop="address">
          <el-input
            v-model="temp.address"
            placeholder="请输入地址"
            :maxlength="200"
            type="textarea"
            :rows="3"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button
          type="primary"
          :loading="submitLoading"
          @click="dialogStatus==='create'?createData():updateData()"
        >
          {{ submitButtonText }}
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.app-container {
  padding: 30px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);

  .filter-container {
    padding-bottom: 30px;

    .filter-item {
      padding: 12px 25px;
      font-size: 14px;
    }
  }

  .box-card {
    margin-bottom: 30px;
    border-radius: 8px;

    ::v-deep .el-card__body {
      padding: 25px;
    }

    .el-table {
      margin: 15px 0;

      th {
        background-color: #f5f7fa;
        padding: 15px 0;

        &.is-leaf {
          border-bottom: 1px solid #EBEEF5;
        }
      }

      td {
        padding: 20px 0;
      }
    }
  }

  .pagination-container {
    padding: 25px 0 10px;
    text-align: right;
  }

  .link-type {
    color: #409EFF;
    cursor: pointer;
    font-size: 14px;

    &:hover {
      color: #66b1ff;
    }
  }

  .margin-left {
    margin-left: 15px;
  }
}

.el-tag {
  padding: 0 15px;
  height: 32px;
  line-height: 30px;
  font-size: 14px;
  border-radius: 4px;
}

.tenant-dialog {
  ::v-deep .el-dialog {
    border-radius: 8px;

    .el-dialog__header {
      padding: 25px 30px 15px;
      border-bottom: 1px solid #EBEEF5;

      .el-dialog__title {
        font-size: 18px;
        font-weight: 500;
      }
    }

    .el-dialog__body {
      padding: 30px 40px;
    }
  }

  .form-container {
    padding: 10px 20px;
  }

  .el-form-item {
    margin-bottom: 35px;

    &:last-child {
      margin-bottom: 10px;
    }

    ::v-deep .el-form-item__label {
      padding-right: 15px;
      font-weight: 500;
    }

    ::v-deep .el-form-item__error {
      padding-top: 4px;
      font-size: 12px;
    }
  }

  .el-row {
    margin-bottom: 10px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .el-col {
    padding-bottom: 5px;
  }

  .status-icon {
    margin-right: 8px;
    font-size: 16px;
  }

  .el-input__prefix {
    font-size: 16px;
    color: #909399;
  }

  .el-textarea__inner {
    font-family: inherit;
    padding: 10px 15px;
  }

  .el-select-dropdown__item {
    display: flex;
    align-items: center;
    padding: 0 30px;
    height: 40px;
  }
}

.dialog-footer {
  text-align: right;
  padding: 20px 0 0;
  border-top: 1px solid #EBEEF5;

  .el-button {
    padding: 12px 25px;
    font-size: 14px;

    & + .el-button {
      margin-left: 20px;
    }
  }
}
</style>

<script>
import { mapState, mapActions } from 'vuex'
import Pagination from '@/components/Pagination'
import { parseTime } from '@/utils'

export default {
  name: 'TenantManagement',
  components: { Pagination },
  filters: {
    parseTime
  },
  data() {
    return {
      listQuery: {
        page: 1,
        limit: 20,
        skip: 0
      },
      temp: {
        id: undefined,
        tenantName: '',
        contactPerson: '',
        phone: '',
        email: '',
        address: '',
        externalId: '',
        status: 'active'
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑租户',
        create: '创建租户'
      },
      submitLoading: false,
      rules: {
        tenantName: [
          { required: true, message: '请输入租户名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        email: [
          { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
        ],
        phone: [
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapState('tenant', {
      list: state => state.list,
      total: state => state.total,
      listLoading: state => state.loading
    }),
    submitButtonText() {
      return this.dialogStatus === 'create' ? '创 建' : '更 新'
    }
  },
  created() {
    this.getList()
  },
  methods: {
    ...mapActions('tenant', [
      'getList',
      'createTenant',
      'updateTenant',
      'deleteTenant'
    ]),
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    handleDialogClose() {
      this.$refs['dataForm'].clearValidate()
      this.submitLoading = false
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.submitLoading = true
          this.createTenant(this.temp).then(() => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建成功',
              type: 'success',
              duration: 2000
            })
          }).finally(() => {
            this.submitLoading = false
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row)
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.submitLoading = true
          const tempData = Object.assign({}, this.temp)
          const id = tempData.id
          delete tempData.id
          delete tempData.createdAt
          delete tempData.updatedAt
          this.updateTenant({ id, data: tempData }).then(() => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
          }).finally(() => {
            this.submitLoading = false
          })
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该租户吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.deleteTenant(row.id).then(() => {
          this.$notify({
            title: '成功',
            message: '删除成功',
            type: 'success',
            duration: 2000
          })
        })
      })
    },
    parseTime(time) {
      return parseTime(time, '{y}-{m}-{d} {h}:{i}')
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        tenantName: '',
        contactPerson: '',
        phone: '',
        email: '',
        address: '',
        externalId: '',
        status: 'active'
      }
    }
  }
}
</script>
