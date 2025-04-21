<template>
  <div class="privacy-container">
    <!-- 顶部装饰 -->
    <div class="top-decoration">
      <div class="decoration-circle circle-1" />
      <div class="decoration-circle circle-2" />
    </div>

    <div class="privacy-content">
      <div class="privacy-header">
        <h1>隐私政策</h1>
        <p class="last-update">最后更新日期：2024年3月15日</p>
      </div>

      <div class="privacy-body">
        <section class="privacy-section">
          <h2>1. 信息收集</h2>
          <p>我们收集的信息包括但不限于：</p>
          <ul>
            <li>您提供的个人信息（如姓名、邮箱、电话等）</li>
            <li>使用服务时产生的数据</li>
            <li>设备信息和日志数据</li>
            <li>Cookie和类似技术收集的信息</li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>2. 信息使用</h2>
          <p>我们使用收集的信息用于：</p>
          <ul>
            <li>提供和改进我们的服务</li>
            <li>与您沟通</li>
            <li>确保服务安全</li>
            <li>遵守法律法规</li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>3. 信息保护</h2>
          <p>我们采取以下措施保护您的信息：</p>
          <ul>
            <li>使用加密技术保护数据传输</li>
            <li>实施访问控制措施</li>
            <li>定期进行安全评估</li>
            <li>对员工进行隐私保护培训</li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>4. 信息共享</h2>
          <p>我们不会在未经您同意的情况下与第三方共享您的个人信息，除非：</p>
          <ul>
            <li>法律法规要求</li>
            <li>保护我们的合法权益</li>
            <li>提供您请求的服务</li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>5. 您的权利</h2>
          <p>您对个人信息享有以下权利：</p>
          <ul>
            <li>访问和查看您的信息</li>
            <li>更正不准确的信息</li>
            <li>删除您的信息</li>
            <li>撤回同意</li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>6. Cookie使用</h2>
          <p>我们使用Cookie来：</p>
          <ul>
            <li>记住您的偏好设置</li>
            <li>提供个性化服务</li>
            <li>分析服务使用情况</li>
            <li>改进服务质量</li>
          </ul>
        </section>

        <section class="privacy-section">
          <h2>7. 联系我们</h2>
          <p>如果您对隐私政策有任何疑问，请通过以下方式联系我们：</p>
          <ul>
            <li>邮箱：privacy@ai-recruitment.com</li>
            <li>电话：400-123-4567</li>
          </ul>
        </section>
      </div>

      <div class="privacy-footer">
        <el-button type="primary" @click="$router.push('/trial-application')">
          返回申请页面
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PrivacyPolicy',
  meta: {
    title: '隐私政策'
  }
}
</script>

<style lang="scss" scoped>
.privacy-container {
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
.privacy-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 0;
  position: relative;
  z-index: 1;
}

.privacy-header {
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

.privacy-body {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 40px;
}

.privacy-section {
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

.privacy-footer {
  text-align: center;
  margin-top: 40px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .privacy-content {
    padding: 20px 0;
  }

  .privacy-header h1 {
    font-size: 24px;
  }

  .privacy-body {
    padding: 20px;
  }

  .privacy-section {
    h2 {
      font-size: 18px;
    }

    p, li {
      font-size: 14px;
    }
  }
}

@media (max-width: 480px) {
  .privacy-content {
    padding: 15px 0;
  }

  .privacy-header h1 {
    font-size: 22px;
  }

  .privacy-body {
    padding: 15px;
  }

  .privacy-section {
    margin-bottom: 20px;

    h2 {
      font-size: 16px;
    }
  }
}
</style>
