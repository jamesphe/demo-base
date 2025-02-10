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
              @click="handleAdd"
            >新增</el-button>
          </div>
          <el-tree
            ref="tree"
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
                  @click.stop="handleEdit(data)"
                >编辑</el-button>
                <el-button
                  type="text"
                  size="mini"
                  @click.stop="handleDelete(data)"
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
            <span>{{ formTitle }}</span>
          </div>
          <el-form ref="form" :model="form" :rules="rules" label-width="100px">
            <el-form-item label="上级部门">
              <el-select v-model="form.parentId" placeholder="请选择上级部门" clearable>
                <el-option
                  v-for="item in parentOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="部门名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入部门名称" />
            </el-form-item>
            <el-form-item label="部门编码" prop="code">
              <el-input v-model="form.code" placeholder="请输入部门编码" />
            </el-form-item>
            <el-form-item label="负责人" prop="leader">
              <el-input v-model="form.leader" placeholder="请输入负责人" />
            </el-form-item>
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入联系电话" />
            </el-form-item>
            <el-form-item label="排序号" prop="orderNum">
              <el-input-number v-model="form.orderNum" :min="0" :max="999" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitForm">确 定</el-button>
              <el-button @click="resetForm">重 置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { getDeptList, addDept, updateDept, deleteDept } from '@/api/organization'

export default {
  name: 'Organization',
  data() {
    return {
      // 部门列表
      deptList: [],
      // 上级部门选项
      parentOptions: [],
      // 树形配置
      defaultProps: {
        children: 'children',
        label: 'name'
      },
      // 表单标题
      formTitle: '添加部门',
      // 表单数据
      form: {
        id: undefined,
        parentId: 0,
        name: '',
        code: '',
        leader: '',
        phone: '',
        orderNum: 0
      },
      // 表单校验规则
      rules: {
        name: [
          { required: true, message: '请输入部门名称', trigger: 'blur' }
        ],
        code: [
          { required: true, message: '请输入部门编码', trigger: 'blur' }
        ]
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
        const response = await getDeptList()
        this.deptList = response.data
        this.generateParentOptions(this.deptList)
      } catch (error) {
        console.error('获取部门列表失败:', error)
      }
    },
    // 生成上级部门选项
    generateParentOptions(deptList, parentId = 0) {
      this.parentOptions = [{ id: 0, name: '顶级部门' }]
      const traverse = (list) => {
        list.forEach(dept => {
          if (dept.id !== this.form.id) { // 排除当前编辑的部门
            this.parentOptions.push({
              id: dept.id,
              name: dept.name
            })
          }
          if (dept.children && dept.children.length > 0) {
            traverse(dept.children)
          }
        })
      }
      traverse(deptList)
    },
    // 点击节点
    handleNodeClick(data) {
      this.form = { ...data }
      this.formTitle = '编辑部门'
      this.generateParentOptions(this.deptList)
    },
    // 新增部门
    handleAdd() {
      this.resetForm()
      this.formTitle = '添加部门'
      this.generateParentOptions(this.deptList)
    },
    // 编辑部门
    handleEdit(data) {
      this.form = { ...data }
      this.formTitle = '编辑部门'
      this.generateParentOptions(this.deptList)
    },
    // 删除部门
    handleDelete(data) {
      if (data.children && data.children.length > 0) {
        this.$message.warning('该部门包含子部门，不能删除')
        return
      }
      this.$confirm('确认删除该部门吗？', '提示', {
        type: 'warning'
      }).then(async() => {
        try {
          await deleteDept(data.id)
          this.$message.success('删除成功')
          this.getDeptList()
          this.resetForm()
        } catch (error) {
          console.error('删除失败:', error)
        }
      }).catch(() => {})
    },
    // 提交表单
    submitForm() {
      this.$refs.form.validate(async(valid) => {
        if (valid) {
          try {
            if (this.form.id) {
              await updateDept(this.form)
              this.$message.success('更新成功')
            } else {
              await addDept(this.form)
              this.$message.success('添加成功')
            }
            this.getDeptList()
            this.resetForm()
          } catch (error) {
            console.error('提交失败:', error)
          }
        }
      })
    },
    // 重置表单
    resetForm() {
      if (this.$refs.form) {
        this.$refs.form.resetFields()
      }
      this.form = {
        id: undefined,
        parentId: 0,
        name: '',
        code: '',
        leader: '',
        phone: '',
        orderNum: 0
      }
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
</style>
