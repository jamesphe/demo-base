<template>
  <div class="app-container">
    <el-form ref="form" :model="positionForm" :rules="rules" label-width="120px">
      <el-card class="box-card">
        <div slot="header">
          <span>基本信息</span>
        </div>
        <el-form-item label="职位名称" prop="title">
          <el-input v-model="positionForm.title" placeholder="请输入职位名称"></el-input>
        </el-form-item>
        <el-form-item label="职位类型" prop="type">
          <el-select v-model="positionForm.type" placeholder="请选择职位类型">
            <el-option label="全职" value="fulltime"></el-option>
            <el-option label="兼职" value="parttime"></el-option>
            <el-option label="实习" value="intern"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="所属部门" prop="department">
          <el-input v-model="positionForm.department" placeholder="请输入所属部门"></el-input>
        </el-form-item>
        <el-form-item label="工作地点" prop="location">
          <el-cascader
            v-model="positionForm.location"
            :options="cityOptions"
            placeholder="请选择工作地点">
          </el-cascader>
        </el-form-item>
      </el-card>

      <el-card class="box-card" style="margin-top: 20px">
        <div slot="header">
          <span>薪资福利</span>
        </div>
        <el-form-item label="薪资范围" prop="salary">
          <el-col :span="8">
            <el-input-number v-model="positionForm.salaryMin" :min="1" placeholder="最低薪资"></el-input-number>
          </el-col>
          <el-col :span="1" style="text-align: center">-</el-col>
          <el-col :span="8">
            <el-input-number v-model="positionForm.salaryMax" :min="1" placeholder="最高薪资"></el-input-number>
          </el-col>
          <el-col :span="4" style="margin-left: 10px">
            <el-select v-model="positionForm.salaryUnit" placeholder="单位">
              <el-option label="K/月" value="month"></el-option>
              <el-option label="K/年" value="year"></el-option>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item label="福利待遇" prop="benefits">
          <el-checkbox-group v-model="positionForm.benefits">
            <el-checkbox label="五险一金">五险一金</el-checkbox>
            <el-checkbox label="年终奖">年终奖</el-checkbox>
            <el-checkbox label="加班补助">加班补助</el-checkbox>
            <el-checkbox label="餐补">餐补</el-checkbox>
            <el-checkbox label="交通补助">交通补助</el-checkbox>
            <el-checkbox label="通讯补贴">通讯补贴</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-card>

      <el-card class="box-card" style="margin-top: 20px">
        <div slot="header">
          <span>要求与职责</span>
        </div>
        <el-form-item label="学历要求" prop="education">
          <el-select v-model="positionForm.education" placeholder="请选择学历要求">
            <el-option label="不限" value="none"></el-option>
            <el-option label="大专" value="college"></el-option>
            <el-option label="本科" value="bachelor"></el-option>
            <el-option label="硕士" value="master"></el-option>
            <el-option label="博士" value="doctor"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="工作经验" prop="experience">
          <el-select v-model="positionForm.experience" placeholder="请选择工作经验">
            <el-option label="不限" value="none"></el-option>
            <el-option label="应届生" value="fresh"></el-option>
            <el-option label="1-3年" value="1-3"></el-option>
            <el-option label="3-5年" value="3-5"></el-option>
            <el-option label="5-10年" value="5-10"></el-option>
            <el-option label="10年以上" value="10+"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="职位描述" prop="description">
          <el-input
            type="textarea"
            :rows="4"
            placeholder="请输入职位描述"
            v-model="positionForm.description">
          </el-input>
        </el-form-item>
        <el-form-item label="任职要求" prop="requirements">
          <el-input
            type="textarea"
            :rows="4"
            placeholder="请输入任职要求"
            v-model="positionForm.requirements">
          </el-input>
        </el-form-item>
      </el-card>

      <div class="form-footer">
        <el-button @click="resetForm">重置</el-button>
        <el-button type="primary" @click="submitForm">发布职位</el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import { publishPosition } from '@/api/position'

export default {
  name: 'PositionPublish',
  data() {
    return {
      positionForm: {
        title: '',
        type: '',
        department: '',
        location: [],
        salaryMin: '',
        salaryMax: '',
        salaryUnit: 'month',
        benefits: [],
        education: '',
        experience: '',
        description: '',
        requirements: ''
      },
      cityOptions: [], // 这里需要添加城市数据
      rules: {
        title: [
          { required: true, message: '请输入职位名称', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择职位类型', trigger: 'change' }
        ],
        department: [
          { required: true, message: '请输入所属部门', trigger: 'blur' }
        ],
        location: [
          { required: true, message: '请选择工作地点', trigger: 'change' }
        ],
        description: [
          { required: true, message: '请输入职位描述', trigger: 'blur' }
        ],
        requirements: [
          { required: true, message: '请输入任职要求', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    resetForm() {
      this.$refs.form.resetFields()
    },
    async submitForm() {
      try {
        await this.$refs.form.validate()
        await publishPosition(this.positionForm)
        this.$message.success('职位发布成功')
        this.resetForm()
      } catch (error) {
        console.error('职位发布失败:', error)
        this.$message.error('职位发布失败，请重试')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}
.box-card {
  margin-bottom: 20px;
}
.form-footer {
  margin-top: 20px;
  text-align: center;
}
</style> 