<template>
  <div class="interview-evaluation-form">
    <!-- 调试信息区域 -->
    <div class="debug-info" style="margin-bottom: 15px; padding: 10px; background-color: #f0f9eb; border: 1px solid #e1f3d8;">
      <p>调试信息：</p>
      <p>processRecord 是否有内容: {{ Boolean(formData.processRecord.trim()) }}</p>
      <p>summary 是否有内容: {{ Boolean(formData.summary.trim()) }}</p>
      <p>strengths 是否有内容: {{ Boolean(formData.strengths.trim()) }}</p>
      <p>weaknesses 是否有内容: {{ Boolean(formData.weaknesses.trim()) }}</p>
      <p>条件计算结果: {{ hasSomeContent }}</p>
    </div>

    <!-- 输入表单 -->
    <div style="margin-bottom: 15px;">
      <p>测试输入:</p>
      <el-input v-model="formData.processRecord" placeholder="processRecord" @input="checkContent"></el-input>
      <el-input v-model="formData.summary" placeholder="summary" @input="checkContent"></el-input>
      <el-input v-model="formData.strengths" placeholder="strengths" @input="checkContent"></el-input>
      <el-input v-model="formData.weaknesses" placeholder="weaknesses" @input="checkContent"></el-input>
    </div>

    <!-- 按钮测试 -->
    <div>
      <el-button @click="resetForm">重置表单</el-button>
      <el-button type="success" :disabled="!hasSomeContent">使用计算值禁用</el-button>
      <el-button type="success" :disabled="!(formData.processRecord.trim() !== '' || 
                                        formData.summary.trim() !== '' || 
                                        formData.strengths.trim() !== '' || 
                                        formData.weaknesses.trim() !== '')">内联条件禁用</el-button>
      <el-button type="warning" @click="debugValues">调试值</el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InterviewEvaluationFormTest',
  data() {
    return {
      formData: {
        processRecord: '',
        summary: '',
        strengths: '',
        weaknesses: ''
      },
      hasSomeContent: false
    }
  },
  methods: {
    checkContent() {
      // 手动计算是否有内容
      this.hasSomeContent = 
        this.formData.processRecord.trim() !== '' || 
        this.formData.summary.trim() !== '' || 
        this.formData.strengths.trim() !== '' || 
        this.formData.weaknesses.trim() !== '';
        
      console.log('内容检查:', {
        processRecord: Boolean(this.formData.processRecord.trim()),
        summary: Boolean(this.formData.summary.trim()),
        strengths: Boolean(this.formData.strengths.trim()),
        weaknesses: Boolean(this.formData.weaknesses.trim()),
        hasSomeContent: this.hasSomeContent
      });
    },
    resetForm() {
      this.formData = {
        processRecord: '',
        summary: '',
        strengths: '',
        weaknesses: ''
      };
      this.hasSomeContent = false;
    },
    debugValues() {
      console.log('=== 调试值 ===');
      console.log('原始值:', JSON.stringify(this.formData));
      console.log('trim后:', {
        processRecord: JSON.stringify(this.formData.processRecord.trim()),
        summary: JSON.stringify(this.formData.summary.trim()),
        strengths: JSON.stringify(this.formData.strengths.trim()),
        weaknesses: JSON.stringify(this.formData.weaknesses.trim())
      });
      
      // 检查不可见字符
      const checkInvisible = (str) => {
        const result = [];
        for(let i=0; i < str.length; i++) {
          result.push(str.charCodeAt(i));
        }
        return result;
      };
      
      console.log('字符编码:', {
        processRecord: checkInvisible(this.formData.processRecord),
        summary: checkInvisible(this.formData.summary),
        strengths: checkInvisible(this.formData.strengths),
        weaknesses: checkInvisible(this.formData.weaknesses)
      });
      
      alert('调试信息已输出到控制台');
    }
  }
}
</script>

<style scoped>
.interview-evaluation-form {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.el-input {
  margin-bottom: 10px;
}

.debug-info {
  margin-bottom: 20px;
}
</style> 