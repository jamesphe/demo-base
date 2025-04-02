<template>
  <div class="company-info">
    <el-form label-width="120px">
      <el-form-item label="企业名称">
        <el-input v-model="companyInfo.name" />
      </el-form-item>

      <el-form-item label="企业代码">
        <el-input v-model="companyInfo.code" disabled />
      </el-form-item>

      <el-form-item label="企业地址">
        <el-input v-model="companyInfo.address" />
      </el-form-item>

      <el-form-item label="联系电话">
        <el-input v-model="companyInfo.phone" />
      </el-form-item>

      <el-form-item label="企业规模">
        <el-select v-model="companyInfo.size" placeholder="请选择">
          <el-option label="1-50人" value="1-50" />
          <el-option label="51-200人" value="51-200" />
          <el-option label="201-500人" value="201-500" />
          <el-option label="501-1000人" value="501-1000" />
          <el-option label="1000人以上" value="1000+" />
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="updateCompanyInfo">保存修改</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'CompanyInfo',
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      companyInfo: {
        name: '示例企业科技有限公司',
        code: 'COMP123456',
        address: '上海市浦东新区XX路XX号',
        phone: '021-12345678',
        size: '51-200'
      }
    }
  },
  methods: {
    updateCompanyInfo() {
      this.$message.success('企业信息更新成功')
    }
  }
}
</script>
