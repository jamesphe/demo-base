<template>
  <div class="app-container">
    <el-row :gutter="20">
      <!-- 左侧部门树 -->
      <el-col :span="8">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>组织机构</span>
            <el-button
              style="float: right; padding: 3px 0"
              type="text"
              icon="el-icon-plus"
              @click="handleAddDept"
            >新增</el-button>
          </div>
          <el-tree
            :data="deptList"
            :props="defaultProps"
            :expand-on-click-node="false"
            default-expand-all
            @node-click="handleNodeClick"
          >
            <span slot-scope="{ node, data }" class="custom-tree-node">
              <span>{{ node.label }}</span>
              <span>
                <el-button
                  type="text"
                  size="mini"
                  @click.stop="handleEditDept(data)"
                >编辑</el-button>
                <el-button
                  type="text"
                  size="mini"
                  @click.stop="handleDeleteDept(data)"
                >删除</el-button>
              </span>
            </span>
          </el-tree>
        </el-card>
      </el-col>

      <!-- 右侧详情 -->
      <el-col :span="16">
        <el-card>
          <div slot="header" class="clearfix">
            <span>{{ currentDept.name || '部门详情' }}</span>
          </div>
          <el-form v-if="currentDept.id" :model="currentDept" label-width="100px">
            <el-form-item label="部门名称">
              <span>{{ currentDept.name }}</span>
            </el-form-item>
            <el-form-item label="部门编码">
              <span>{{ currentDept.code }}</span>
            </el-form-item>
            <el-form-item label="上级部门">
              <span>{{ currentDept.parentName }}</span>
            </el-form-item>
            <el-form-item label="负责人">
              <span>{{ currentDept.leader }}</span>
            </el-form-item>
            <el-form-item label="联系电话">
              <span>{{ currentDept.phone }}</span>
            </el-form-item>
            <el-form-item label="创建时间">
              <span>{{ currentDept.createTime }}</span>
            </el-form-item>
          </el-form>
          <div v-else class="empty-text">
            请选择部门查看详情
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 部门编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入部门编码" />
        </el-form-item>
        <el-form-item label="上级部门" prop="parentId">
          <el-cascader
            v-model="form.parentId"
            :options="deptList"
            :props="{ checkStrictly: true, value: 'id', label: 'name' }"
            clearable
            placeholder="请选择上级部门"
          />
        </el-form-item>
        <el-form-item label="负责人" prop="leader">
          <el-input v-model="form.leader" placeholder="请输入负责人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitForm">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'Organization',
  data() {
    return {
      deptList: [],
      currentDept: {},
      defaultProps: {
        children: 'children',
        label: 'name'
      },
      dialogVisible: false,
      dialogTitle: '',
      form: {
        id: undefined,
        name: undefined,
        code: undefined,
        parentId: undefined,
        leader: undefined,
        phone: undefined
      },
      rules: {
        name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
        code: [{ required: true, message: '请输入部门编码', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getDeptList()
  },
  methods: {
    // 获取部门列表
    async getDeptList() {
      try {
        const response = await request({
          url: '/vue-element-admin/department/list',
          method: 'get'
        })
        this.deptList = response.data
      } catch (error) {
        console.error('获取部门列表失败:', error)
      }
    },

    // 点击树节点
    handleNodeClick(data) {
      this.currentDept = data
    },

    // 新增部门
    handleAddDept() {
      this.dialogTitle = '新增部门'
      this.form = {
        id: undefined,
        name: undefined,
        code: undefined,
        parentId: undefined,
        leader: undefined,
        phone: undefined
      }
      this.dialogVisible = true
    },

    // 编辑部门
    handleEditDept(data) {
      this.dialogTitle = '编辑部门'
      this.form = { ...data }
      this.dialogVisible = true
    },

    // 删除部门
    handleDeleteDept(data) {
      this.$confirm('确认删除该部门吗？', '警告', {
        type: 'warning'
      }).then(async() => {
        try {
          await request({
            url: `/vue-element-admin/department/${data.id}`,
            method: 'delete'
          })
          this.$message.success('删除成功')
          this.getDeptList()
          this.currentDept = {}
        } catch (error) {
          console.error('删除失败:', error)
        }
      })
    },

    // 提交表单
    submitForm() {
      this.$refs.form.validate(async valid => {
        if (valid) {
          try {
            if (this.form.id) {
              await request({
                url: '/vue-element-admin/department',
                method: 'put',
                data: this.form
              })
              this.$message.success('修改成功')
            } else {
              await request({
                url: '/vue-element-admin/department',
                method: 'post',
                data: this.form
              })
              this.$message.success('添加成功')
            }
            this.dialogVisible = false
            this.getDeptList()
          } catch (error) {
            console.error('提交失败:', error)
          }
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.empty-text {
  text-align: center;
  color: #909399;
  font-size: 14px;
  line-height: 200px;
}
</style>
