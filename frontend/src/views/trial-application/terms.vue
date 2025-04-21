<template>
  <div class="terms-container">
    <!-- 顶部装饰 -->
    <div class="top-decoration">
      <div class="decoration-circle circle-1" />
      <div class="decoration-circle circle-2" />
    </div>

    <div class="terms-content">
      <div class="terms-header">
        <h1>服务条款</h1>
        <p class="last-update">最后更新日期：2024年3月15日</p>
      </div>

      <div class="terms-body">
        <section class="terms-section">
          <h2>1. 服务说明</h2>
          <p>本服务条款（以下简称"条款"）是您与AI招聘助手（以下简称"我们"）之间关于使用我们的服务所达成的协议。通过使用我们的服务，您同意遵守本条款的所有规定。</p>
        </section>

        <section class="terms-section">
          <h2>2. 服务内容</h2>
          <p>我们提供的服务包括但不限于：</p>
          <ul>
            <li>智能简历解析</li>
            <li>候选人评估</li>
            <li>职位匹配</li>
            <li>面试辅助</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2>3. 用户责任</h2>
          <p>作为用户，您同意：</p>
          <ul>
            <li>提供真实、准确、完整的个人信息</li>
            <li>保护您的账户安全</li>
            <li>遵守相关法律法规</li>
            <li>不进行任何可能损害我们服务的行为</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2>4. 知识产权</h2>
          <p>我们保留所有与本服务相关的知识产权。未经我们书面许可，您不得复制、修改、分发或使用我们的任何内容。</p>
        </section>

        <section class="terms-section">
          <h2>5. 免责声明</h2>
          <p>我们不对以下情况承担责任：</p>
          <ul>
            <li>服务中断或延迟</li>
            <li>数据丢失或损坏</li>
            <li>第三方服务的问题</li>
            <li>不可抗力因素</li>
          </ul>
        </section>

        <section class="terms-section">
          <h2>6. 条款修改</h2>
          <p>我们保留随时修改本条款的权利。修改后的条款将在网站上公布，继续使用我们的服务即表示您接受修改后的条款。</p>
        </section>

        <section class="terms-section">
          <h2>7. 联系我们</h2>
          <p>如果您对本条款有任何疑问，请通过以下方式联系我们：</p>
          <ul>
            <li>邮箱：support@ai-recruitment.com</li>
            <li>电话：400-123-4567</li>
          </ul>
        </section>
      </div>

      <div class="terms-footer">
        <el-button type="primary" @click="$router.push('/trial-application')">
          返回申请页面
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TermsOfService',
  meta: {
    title: '服务条款'
  }
}
</script>

<style lang="scss" scoped>
.terms-container {
  max-width: 100%;
  min-height: 100vh;
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

/* 内容区域 */
.terms-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 0;
  position: relative;
  z-index: 1;
}

.terms-header {
  text-align: center;
  margin-bottom: 40px;

  h1 {
    font-size: 32px;
    color: #303133;
    margin-bottom: 10px;
  }

  .last-update {
    color: #909399;
    font-size: 14px;
  }
}

.terms-body {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 40px;
}

.terms-section {
  margin-bottom: 30px;

  h2 {
    font-size: 20px;
    color: #303133;
    margin-bottom: 15px;
    position: relative;
    padding-left: 15px;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 4px;
      height: 20px;
      background: #409EFF;
      border-radius: 2px;
    }
  }

  p {
    color: #606266;
    line-height: 1.8;
    margin-bottom: 15px;
  }

  ul {
    list-style-type: none;
    padding-left: 20px;
    margin-bottom: 15px;

    li {
      position: relative;
      padding-left: 10px;
      margin-bottom: 10px;
      color: #606266;
      line-height: 1.6;

      &::before {
        content: '•';
        position: absolute;
        left: 0;
        color: #409EFF;
      }
    }
  }
}

.terms-footer {
  text-align: center;
  margin-top: 40px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .terms-content {
    padding: 20px 0;
  }

  .terms-header h1 {
    font-size: 24px;
  }

  .terms-body {
    padding: 20px;
  }

  .terms-section {
    h2 {
      font-size: 18px;
    }

    p, li {
      font-size: 14px;
    }
  }
}

@media (max-width: 480px) {
  .terms-content {
    padding: 15px 0;
  }

  .terms-header h1 {
    font-size: 22px;
  }

  .terms-body {
    padding: 15px;
  }

  .terms-section {
    margin-bottom: 20px;

    h2 {
      font-size: 16px;
    }
  }
}
</style>
