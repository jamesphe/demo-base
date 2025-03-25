<template>
  <div class="trial-application-container">
    <!-- 顶部背景装饰 -->
    <div class="top-decoration">
      <div class="decoration-circle circle-1" />
      <div class="decoration-circle circle-2" />
      <div class="decoration-circle circle-3" />
    </div>

    <div class="trial-header">
      <h1>申请免费试用 <span class="highlight">AI招聘助手</span></h1>
      <p class="description">填写以下信息，我们将在1-2个工作日内审核您的申请</p>
      <div class="trial-benefits">
        <div class="benefit-item">
          <i class="el-icon-time" />
          <span>14天完整功能体验</span>
        </div>
        <div class="benefit-item">
          <i class="el-icon-user" />
          <span>专属客服支持</span>
        </div>
        <div class="benefit-item">
          <i class="el-icon-data-analysis" />
          <span>AI招聘全流程</span>
        </div>
      </div>
    </div>

    <el-card class="form-card">
      <div class="card-header">
        <i class="el-icon-edit-outline" />
        <span>申请表单</span>
      </div>

      <el-form
        ref="trialForm"
        :model="formData"
        :rules="rules"
        label-width="120px"
        class="trial-form"
        label-position="top"
      >
        <h3 class="form-section-title"><i class="el-icon-user" /> 基本信息</h3>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="公司名称" prop="companyName">
              <el-input
                v-model="formData.companyName"
                placeholder="请输入公司名称"
                prefix-icon="el-icon-office-building"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="联系人" prop="contactName">
              <el-input
                v-model="formData.contactName"
                placeholder="请输入联系人姓名"
                prefix-icon="el-icon-user"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="联系电话" prop="contactPhone">
              <el-input
                v-model="formData.contactPhone"
                placeholder="请输入联系电话"
                prefix-icon="el-icon-phone"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="联系邮箱" prop="contactEmail">
              <el-input
                v-model="formData.contactEmail"
                placeholder="请输入联系邮箱"
                prefix-icon="el-icon-message"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <h3 class="form-section-title"><i class="el-icon-office-building" /> 业务信息</h3>
        <el-form-item label="公司规模">
          <el-select v-model="formData.companySize" placeholder="请选择公司规模" style="width: 100%">
            <el-option label="1-10人" value="1-10" />
            <el-option label="11-50人" value="11-50" />
            <el-option label="51-200人" value="51-200" />
            <el-option label="201-500人" value="201-500" />
            <el-option label="501-1000人" value="501-1000" />
            <el-option label="1000人以上" value="1000+" />
          </el-select>
        </el-form-item>

        <el-form-item label="业务描述" prop="businessDescription">
          <el-input
            v-model="formData.businessDescription"
            type="textarea"
            rows="4"
            placeholder="请简要描述您的业务，例如：公司规模、主要业务方向、目前招聘情况等"
          />
        </el-form-item>

        <el-form-item label="申请原因" prop="applicationReason">
          <el-input
            v-model="formData.applicationReason"
            type="textarea"
            rows="4"
            placeholder="请说明申请试用的原因，例如：希望解决的招聘痛点、对AI招聘的期望等"
          />
        </el-form-item>

        <div class="agreement-section">
          <el-checkbox v-model="agreement">我已阅读并同意<a href="#">《服务条款》</a>和<a href="#">《隐私政策》</a></el-checkbox>
        </div>

        <div class="form-actions">
          <el-button
            type="primary"
            :loading="loading"
            :disabled="!agreement"
            class="submit-btn"
            @click="submitApplication"
          >
            <i class="el-icon-check" /> 提交申请
          </el-button>
          <el-button plain @click="$router.push('/')">
            <i class="el-icon-back" /> 返回首页
          </el-button>
        </div>
      </el-form>
    </el-card>

    <div class="trial-features">
      <div class="section-header">
        <h3>试用期间您将获得以下功能</h3>
        <div class="section-divider">
          <span />
        </div>
      </div>

      <div class="features-grid">
        <div class="feature-item">
          <div class="feature-icon">
            <i class="el-icon-document" />
          </div>
          <h4>智能简历解析</h4>
          <p>自动提取简历信息，支持多种格式，准确率高达95%</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">
            <i class="el-icon-data-analysis" />
          </div>
          <h4>智能评分系统</h4>
          <p>多维度评估候选人能力，提供客观量化的评价标准</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">
            <i class="el-icon-connection" />
          </div>
          <h4>智能人岗匹配</h4>
          <p>精准匹配职位要求与候选人能力，提高招聘效率</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">
            <i class="el-icon-chat-dot-round" />
          </div>
          <h4>智能面试助手</h4>
          <p>自动生成个性化面试题库，助力高效面试流程</p>
        </div>
      </div>
    </div>

    <!-- 客户评价部分 -->
    <div class="testimonials">
      <div class="section-header">
        <h3>客户评价</h3>
        <div class="section-divider">
          <span />
        </div>
      </div>

      <div class="testimonials-grid">
        <div class="testimonial-item">
          <div class="testimonial-avatar">
            <img src="https://randomuser.me/api/portraits/men/32.jpg" alt="用户头像">
          </div>
          <div class="testimonial-content">
            <div class="quote-icon"><i class="el-icon-chat-round" /></div>
            <p class="quote-text">"AI招聘助手帮我们节省了70%的简历筛选时间，大大提高了招聘效率。"</p>
            <div class="quote-author">
              <strong>张经理</strong> - 某科技公司HR总监
            </div>
            <div class="rating">
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
            </div>
          </div>
        </div>

        <div class="testimonial-item">
          <div class="testimonial-avatar">
            <img src="https://randomuser.me/api/portraits/women/44.jpg" alt="用户头像">
          </div>
          <div class="testimonial-content">
            <div class="quote-icon"><i class="el-icon-chat-round" /></div>
            <p class="quote-text">"智能人岗匹配功能非常准确，帮我们找到了最合适的候选人。"</p>
            <div class="quote-author">
              <strong>李总监</strong> - 某互联网公司招聘负责人
            </div>
            <div class="rating">
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
            </div>
          </div>
        </div>

        <div class="testimonial-item">
          <div class="testimonial-avatar">
            <img src="https://randomuser.me/api/portraits/men/68.jpg" alt="用户头像">
          </div>
          <div class="testimonial-content">
            <div class="quote-icon"><i class="el-icon-chat-round" /></div>
            <p class="quote-text">"面试助手生成的问题非常有针对性，帮助我们更全面地评估候选人。"</p>
            <div class="quote-author">
              <strong>王经理</strong> - 某金融公司HR经理
            </div>
            <div class="rating">
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
              <i class="el-icon-star-on" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部CTA -->
    <div class="bottom-cta">
      <h3>立即开始您的AI招聘之旅</h3>
      <p>14天免费试用，无任何费用</p>
      <el-button type="primary" size="large" class="cta-button" @click="scrollToForm">
        免费试用
      </el-button>
    </div>
  </div>
</template>

<script>
import { applyForTrial } from '@/api/user'

export default {
  name: 'TrialApplication',
  data() {
    return {
      loading: false,
      agreement: false,
      formData: {
        companyName: '',
        contactName: '',
        contactPhone: '',
        contactEmail: '',
        companySize: '',
        businessDescription: '',
        applicationReason: ''
      },
      rules: {
        companyName: [
          { required: true, message: '请输入公司名称', trigger: 'blur' }
        ],
        contactName: [
          { required: true, message: '请输入联系人姓名', trigger: 'blur' }
        ],
        contactPhone: [
          { required: true, message: '请输入联系电话', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
        ],
        contactEmail: [
          { required: true, message: '请输入联系邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
        ],
        businessDescription: [
          { required: true, message: '请描述您的业务', trigger: 'blur' }
        ],
        applicationReason: [
          { required: true, message: '请说明申请原因', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    scrollToForm() {
      document.querySelector('.form-card').scrollIntoView({ behavior: 'smooth' })
    },
    submitApplication() {
      if (!this.agreement) {
        this.$message.warning('请先阅读并同意服务条款和隐私政策')
        return
      }

      this.$refs.trialForm.validate(async(valid) => {
        if (valid) {
          this.loading = true
          try {
            await applyForTrial(this.formData)
            this.$message.success('申请提交成功，我们将尽快审核')
            this.$router.push('/')
          } catch (error) {
            this.$message.error(error.message || '申请提交失败，请稍后重试')
          } finally {
            this.loading = false
          }
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
/* 基础样式 */
.trial-application-container {
  max-width: 100%;
  padding: 0 15px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  background: #f9fafc;
}

/* 顶部装饰 */
.top-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 300px;
  overflow: hidden;
  z-index: 0;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1) 0%, rgba(83, 168, 255, 0.1) 100%);
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  left: -100px;
}

.circle-2 {
  width: 200px;
  height: 200px;
  top: -50px;
  right: -50px;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 100px;
  right: 100px;
}

/* 标题区域 */
.trial-header {
  text-align: center;
  padding: 50px 0 30px;
  position: relative;
  z-index: 1;
}

h1 {
  font-size: 32px;
  margin-bottom: 15px;
  color: #303133;
  position: relative;
  display: inline-block;
}

.highlight {
  color: #409EFF;
  position: relative;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 6px;
  background: rgba(64, 158, 255, 0.2);
  z-index: -1;
}

.description {
  font-size: 18px;
  color: #606266;
  margin-bottom: 30px;
}

/* 试用权益 */
.trial-benefits {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 40px;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: white;
  border-radius: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.benefit-item i {
  font-size: 20px;
  color: #409EFF;
}

/* 表单卡片 */
.form-card {
  max-width: 900px;
  margin: 0 auto 60px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 1;
}

.card-header {
  background: linear-gradient(135deg, #409EFF 0%, #53a8ff 100%);
  color: white;
  padding: 15px 20px;
  border-radius: 12px 12px 0 0;
  font-size: 18px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 10px;
}

.trial-form {
  padding: 30px 20px;
}

.form-section-title {
  font-size: 18px;
  margin: 20px 0;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-section-title i {
  color: #409EFF;
}

/* 协议同意 */
.agreement-section {
  margin: 30px 0;
}

.agreement-section a {
  color: #409EFF;
  text-decoration: none;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.submit-btn {
  padding: 12px 30px;
  font-size: 16px;
}

/* 功能特性 */
.trial-features {
  max-width: 1200px;
  margin: 0 auto 60px;
  padding: 0 20px;
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-header h3 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 15px;
}

.section-divider {
  display: flex;
  justify-content: center;
  align-items: center;
}

.section-divider span {
  width: 60px;
  height: 4px;
  background: #409EFF;
  border-radius: 2px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-item {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  text-align: center;
}

.feature-item:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  transition: all 0.3s;
}

.feature-item:hover .feature-icon {
  background: #409EFF;
  transform: scale(1.1);
}

.feature-icon i {
  font-size: 32px;
  color: #409EFF;
  transition: all 0.3s;
}

.feature-item:hover .feature-icon i {
  color: white;
}

.feature-item h4 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #303133;
}

.feature-item p {
  color: #606266;
  font-size: 15px;
  line-height: 1.6;
}

/* 底部CTA */
.bottom-cta {
  margin: 70px auto;
  text-align: center;
  background: linear-gradient(135deg, #409EFF 0%, #53a8ff 100%);
  padding: 50px 20px;
  border-radius: 12px;
  color: white;
  max-width: 900px;
}

.bottom-cta h3 {
  font-size: 28px;
  margin-bottom: 15px;
}

.bottom-cta p {
  font-size: 16px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.cta-button {
  padding: 15px 40px;
  font-size: 18px;
  border: 2px solid white;
  background: transparent;
  transition: all 0.3s;
}

.cta-button:hover {
  background: white;
  color: #409EFF;
}

/* 客户评价区域 */
.testimonials {
  max-width: 1200px;
  margin: 70px auto;
  padding: 0 20px;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

.testimonial-item {
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.testimonial-item:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
}

.testimonial-avatar {
  width: 100%;
  height: 120px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f0ff 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.testimonial-avatar img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.testimonial-content {
  padding: 25px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.quote-icon {
  color: #409EFF;
  font-size: 24px;
  margin-bottom: 15px;
}

.quote-text {
  font-size: 16px;
  line-height: 1.6;
  color: #303133;
  margin-bottom: 20px;
  flex-grow: 1;
  position: relative;
  padding-left: 10px;
  border-left: 3px solid rgba(64, 158, 255, 0.2);
}

.quote-author {
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
}

.rating {
  color: #F7BA2A;
  font-size: 16px;
}

/* 响应式设计优化 */
@media (max-width: 768px) {
  .trial-application-container {
    padding: 0 10px;
  }

  h1 {
    font-size: 24px;
    line-height: 1.3;
  }

  .description {
    font-size: 16px;
    padding: 0 15px;
  }

  .trial-benefits {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }

  .benefit-item {
    width: 100%;
    max-width: 280px;
    justify-content: center;
  }

  .form-card {
    margin-bottom: 40px;
    border-radius: 8px;
  }

  .card-header {
    padding: 12px 15px;
    font-size: 16px;
    border-radius: 8px 8px 0 0;
  }

  .trial-form {
    padding: 20px 15px;
  }

  .form-section-title {
    font-size: 16px;
    margin: 15px 0;
  }

  .form-actions {
    flex-direction: column;
    gap: 10px;
  }

  .form-actions .el-button {
    width: 100%;
  }

  .section-header h3 {
    font-size: 22px;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .feature-item {
    padding: 20px 15px;
  }

  .feature-icon {
    width: 60px;
    height: 60px;
  }

  .feature-icon i {
    font-size: 28px;
  }

  .feature-item h4 {
    font-size: 18px;
  }

  .feature-item p {
    font-size: 14px;
  }

  .bottom-cta {
    margin: 40px auto;
    padding: 30px 15px;
    border-radius: 8px;
  }

  .bottom-cta h3 {
    font-size: 22px;
  }

  .bottom-cta p {
    font-size: 14px;
  }

  .cta-button {
    padding: 12px 30px;
    font-size: 16px;
    width: 100%;
  }

  /* 调整表单标签位置 */
  :deep(.el-form-item__label) {
    padding-bottom: 5px;
  }

  /* 调整输入框高度 */
  :deep(.el-input__inner) {
    height: 40px;
  }

  .testimonials {
    margin: 50px auto;
  }

  .testimonials-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .testimonial-item {
    flex-direction: row;
    align-items: center;
    height: auto;
  }

  .testimonial-avatar {
    width: 100px;
    height: 100%;
    flex-shrink: 0;
  }

  .testimonial-avatar img {
    width: 60px;
    height: 60px;
  }

  .testimonial-content {
    padding: 15px;
  }

  .quote-icon {
    font-size: 18px;
    margin-bottom: 10px;
  }

  .quote-text {
    font-size: 14px;
    margin-bottom: 10px;
  }
}

/* 超小屏幕优化 */
@media (max-width: 480px) {
  .trial-header {
    padding: 30px 0 20px;
  }

  h1 {
    font-size: 22px;
  }

  .description {
    font-size: 14px;
    margin-bottom: 20px;
  }

  .benefit-item {
    padding: 8px 15px;
    font-size: 14px;
  }

  .benefit-item i {
    font-size: 18px;
  }

  .form-card {
    margin-bottom: 30px;
  }

  .agreement-section {
    margin: 20px 0;
    font-size: 13px;
  }

  .feature-item {
    padding: 15px;
  }

  .bottom-cta {
    padding: 25px 15px;
  }

  .testimonial-item {
    flex-direction: column;
  }

  .testimonial-avatar {
    width: 100%;
    height: 100px;
  }

  .testimonial-content {
    padding: 15px;
  }

  .quote-text {
    border-left: none;
    padding-left: 0;
    text-align: center;
  }

  .quote-author, .rating {
    text-align: center;
  }
}
</style>
