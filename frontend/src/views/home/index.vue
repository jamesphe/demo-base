<template>
  <div class="home-container">
    <!-- 添加鼠标跟随效果 -->
    <div ref="follower" class="cursor-follower" />

    <!-- 添加背景动态网格 -->
    <div class="background-grid" />

    <!-- 在 Hero Section 添加动态粒子效果 -->
    <div ref="particles" class="particles-container" />

    <!-- 添加滚动进度指示器 -->
    <div class="scroll-progress" :style="{ width: scrollProgress + '%' }" />

    <!-- 导航栏 -->
    <nav-header
      :is-scrolled="isScrolled"
      :active-section="activeSection"
      :is-logged-in="isLoggedIn"
      :user-info="userInfo"
      @command="handleCommand"
    />

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-background-shapes">
        <div class="shape shape-1" />
        <div class="shape shape-2" />
        <div class="shape shape-3" />
      </div>
      <div class="hero-content">
        <h1 class="animate__animated animate__fadeInDown">
          AI 驱动的智能招聘管理平台
        </h1>
        <h2 class="animate__animated animate__fadeInUp animate__delay-1s">
          基于 Deepseek 大语言模型，为企业提供智能化招聘解决方案
        </h2>
        <div class="hero-buttons animate__animated animate__fadeInUp animate__delay-2s">
          <el-button type="primary" size="large" round @click="startTrial">
            免费试用 14 天
          </el-button>
          <el-button size="large" round class="demo-btn" @click="watchDemo">
            <i class="el-icon-video-play" /> 观看演示
          </el-button>
        </div>
        <div class="hero-stats animate__animated animate__fadeInUp animate__delay-3s">
          <div class="stat-item">
            <div class="stat-number">
              <count-to :start-val="0" :end-val="99" :duration="2500" />%
            </div>
            <div class="stat-label">简历解析准确率</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">
              <count-to :start-val="0" :end-val="85" :duration="2500" />%
            </div>
            <div class="stat-label">人岗匹配精准度</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">
              <count-to :start-val="0" :end-val="70" :duration="2500" />%
            </div>
            <div class="stat-label">平均效率提升</div>
          </div>
        </div>
      </div>
      <!-- 将滚动提示移到这里 -->
      <div class="scroll-hint">
        <i class="el-icon-arrow-down" />
      </div>
    </section>

    <!-- 核心功能展示 -->
    <section id="features" class="features">
      <div class="section-background">
        <div class="bg-gradient" />
        <div class="bg-pattern" />
      </div>
      <h2 v-scroll-animation class="section-title">核心功能</h2>
      <div class="feature-grid">
        <div
          v-for="feature in features"
          :key="feature.id"
          v-scroll-animation
          class="feature-card"
        >
          <div class="feature-icon">
            <i :class="feature.icon" />
          </div>
          <h3>{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.description }}</p>
          <div class="feature-points">
            <div
              v-for="(point, index) in feature.points"
              :key="index"
              class="point-item"
            >
              <i class="el-icon-check" />
              <span>{{ point }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- AI 能力展示 -->
    <section id="ai-capabilities" class="ai-capabilities">
      <h2 v-scroll-animation class="section-title">AI 智能能力</h2>
      <div class="capabilities-container">
        <div
          v-for="cap in aiCapabilities"
          :key="cap.id"
          v-scroll-animation
          class="capability"
        >
          <div class="capability-icon">
            <i :class="cap.icon" />
          </div>
          <div class="capability-content">
            <h3>{{ cap.title }}</h3>
            <p>{{ cap.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 订阅计划 -->
    <section id="pricing" class="pricing">
      <h2 v-scroll-animation class="section-title">订阅计划</h2>
      <div class="plan-container">
        <div
          v-for="plan in plans"
          :key="plan.id"
          v-scroll-animation
          class="plan-card"
          :class="{ 'recommended': plan.recommended }"
        >
          <div class="plan-header">
            <h3>{{ plan.name }}</h3>
            <div class="price">
              <span class="amount">¥{{ plan.price }}</span>
              <span class="period">/月</span>
            </div>
          </div>
          <ul class="plan-features">
            <li v-for="feature in plan.features" :key="feature">
              <i class="el-icon-check" />
              {{ feature }}
            </li>
          </ul>
          <el-button
            :type="plan.recommended ? 'primary' : 'default'"
            class="subscribe-btn"
          >
            立即订阅
          </el-button>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-section">
          <h3>联系我们</h3>
          <p><i class="el-icon-location" /> 地址：北京市朝阳区xxx大厦</p>
          <p><i class="el-icon-phone" /> 电话：400-xxx-xxxx</p>
          <p><i class="el-icon-message" /> 邮箱：support@airecruitment.com</p>
        </div>
        <div class="footer-section">
          <h3>关注我们</h3>
          <div class="social-links">
            <a href="#"><i class="el-icon-platform-eleme" /></a>
            <a href="#"><i class="el-icon-s-platform" /></a>
            <a href="#"><i class="el-icon-share" /></a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2024 AI招聘助手. All rights reserved.</p>
      </div>
    </footer>

    <!-- 演示视频对话框 -->
    <el-dialog
      title="产品演示"
      :visible.sync="dialogVisible"
      width="70%"
      class="demo-dialog"
      :before-close="handleClose"
    >
      <div class="video-container">
        <div class="video-placeholder">
          <i class="el-icon-video-play" />
          <p>点击播放演示视频</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import CountTo from 'vue-count-to'
import 'animate.css'
import NavHeader from '@/components/layout/NavHeader.vue'
import Vue from 'vue'

// 全局注册 NavHeader 组件
Vue.component('NavHeader', NavHeader)

export default {
  name: 'HomePage',
  components: {
    CountTo,
    NavHeader
  },
  directives: {
    'scroll-animation': {
      inserted: function(el) {
        el.classList.add('scroll-animation')
        const observer = new IntersectionObserver(entries => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              setTimeout(() => {
                el.classList.add('animate__animated', 'animate__fadeInUp')
              }, 100)
              observer.unobserve(el)
            }
          })
        }, {
          threshold: 0.1,
          rootMargin: '0px 0px 50px 0px'
        })
        observer.observe(el)
      }
    }
  },
  data() {
    return {
      isLoggedIn: false,
      userInfo: {},
      dialogVisible: false,
      isScrolled: false,
      scrollProgress: 0,
      activeSection: 'features',
      features: [
        {
          id: 1,
          icon: 'el-icon-document',
          title: '智能简历解析',
          description: '基于深度学习的简历解析技术，准确提取简历信息，支持多种格式',
          points: [
            '支持多种简历格式解析',
            '95% 以上信息提取准确率',
            '自动标准化处理',
            '批量处理能力'
          ]
        },
        {
          id: 2,
          icon: 'el-icon-data-analysis',
          title: '智能评分系统',
          description: '多维度评估候选人能力，生成量化评分报告',
          points: [
            '多维度能力评估',
            '个性化评分权重',
            '可视化评分报告',
            '历史数据对比'
          ]
        },
        {
          id: 3,
          icon: 'el-icon-connection',
          title: '智能人岗匹配',
          description: '基于深度语义理解，精准匹配职位要求与候选人能力',
          points: [
            '语义级匹配算法',
            '智能相似度计算',
            '可解释性分析',
            '批量匹配推荐'
          ]
        },
        {
          id: 4,
          icon: 'el-icon-chat-dot-round',
          title: '智能面试助手',
          description: '自动生成个性化面试题库，辅助面试官高效决策',
          points: [
            '智能题库生成',
            '面试流程指导',
            '实时反馈建议',
            '面试评估报告'
          ]
        }
      ],
      aiCapabilities: [
        {
          id: 1,
          icon: 'el-icon-cpu',
          title: '深度语义理解',
          description: '基于 Deepseek 大语言模型，深度理解简历内容与职位要求'
        },
        {
          id: 2,
          icon: 'el-icon-rank',
          title: '智能人才画像',
          description: '多维度分析候选人能力特征，构建完整人才画像'
        },
        {
          id: 3,
          icon: 'el-icon-data-line',
          title: '智能推荐系统',
          description: '基于历史招聘数据，为企业精准推荐合适人选'
        }
      ],
      plans: [
        {
          id: 1,
          name: '基础版',
          price: 999,
          features: [
            '简历智能解析',
            '基础人才画像',
            '简单职位匹配',
            '最多 3 个用户',
            '每月 100 份简历',
            '基础数据报表'
          ]
        },
        {
          id: 2,
          name: '专业版',
          price: 2999,
          recommended: true,
          features: [
            '全部基础版功能',
            '高级人才画像',
            '智能职位匹配',
            '最多 10 个用户',
            '每月 1000 份简历',
            '高级数据分析'
          ]
        },
        {
          id: 3,
          name: '企业版',
          price: 4999,
          features: [
            '全部专业版功能',
            'API 接口调用',
            '私有化部署',
            '无限用户数量',
            '无限简历解析',
            '专属客户经理'
          ]
        }
      ]
    }
  },
  created() {
    // 移除不必要的用户信息获取
    window.addEventListener('scroll', this.handleScroll)
  },
  destroyed() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  mounted() {
    // 只在非移动设备上添加鼠标跟随效果
    if (window.innerWidth > 768) {
      document.addEventListener('mousemove', this.handleMouseMove)
    }

    // 添加滚动进度监听
    window.addEventListener('scroll', this.handleScroll)
    this.initScrollSpy()

    // 添加触摸滑动支持
    this.initTouchSwipe()

    // 添加粒子效果
    this.initParticles()
  },
  beforeDestroy() {
    // 只在非移动设备上移除鼠标跟随效果
    if (window.innerWidth > 768) {
      document.removeEventListener('mousemove', this.handleMouseMove)
    }

    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    handleScroll() {
      this.isScrolled = window.scrollY > 50
      const winScroll = document.documentElement.scrollTop
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight
      this.scrollProgress = (winScroll / height) * 100
    },
    startTrial() {
      this.$router.push('/trial-application')
    },
    handleCommand(command) {
      if (command === 'logout') {
        this.$store.dispatch('user/logout').then(() => {
          this.$router.push('/login')
        })
      } else if (command === 'dashboard') {
        this.$router.push('/dashboard')
      } else if (command === 'profile') {
        this.$router.push('/profile')
      }
    },
    watchDemo() {
      this.dialogVisible = true
    },
    handleClose(done) {
      this.$confirm('确认关闭？')
        .then(_ => {
          done()
        })
        .catch(_ => {})
    },
    handleMouseMove(e) {
      if (this.$refs.follower) {
        this.$refs.follower.style.transform = `translate(${e.clientX - 10}px, ${e.clientY - 10}px)`
      }
    },
    initScrollSpy() {
      const sections = ['features', 'ai-capabilities', 'pricing']
      window.addEventListener('scroll', () => {
        const scrollPosition = window.scrollY + 100
        sections.forEach(section => {
          const element = document.getElementById(section)
          if (element) {
            const { offsetTop, offsetHeight } = element
            if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
              this.activeSection = section
            }
          }
        })
      })
    },
    initTouchSwipe() {
      let startX, startY, distX, distY
      const threshold = 150 // 最小滑动距离
      const restraint = 100 // 最大垂直移动距离
      const sections = ['features', 'ai-capabilities', 'pricing']

      document.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX
        startY = e.touches[0].clientY
      }, false)

      document.addEventListener('touchend', (e) => {
        distX = e.changedTouches[0].clientX - startX
        distY = e.changedTouches[0].clientY - startY

        if (Math.abs(distX) >= threshold && Math.abs(distY) <= restraint) {
          // 确定当前部分的索引
          const currentIndex = sections.indexOf(this.activeSection)
          if (currentIndex !== -1) {
            if (distX > 0) {
              // 向右滑动，前往上一部分
              if (currentIndex > 0) {
                const prevSection = sections[currentIndex - 1]
                document.getElementById(prevSection).scrollIntoView({ behavior: 'smooth' })
              }
            } else {
              // 向左滑动，前往下一部分
              if (currentIndex < sections.length - 1) {
                const nextSection = sections[currentIndex + 1]
                document.getElementById(nextSection).scrollIntoView({ behavior: 'smooth' })
              }
            }
          }
        }
      }, false)
    },
    initParticles() {
      if (!this.$refs.particles) return

      const particlesContainer = this.$refs.particles
      const isMobile = window.innerWidth < 768

      // 清空现有粒子
      particlesContainer.innerHTML = ''

      // 如果是移动设备，减少粒子数量
      const particlesCount = isMobile ? 10 : 50

      for (let i = 0; i < particlesCount; i++) {
        const particle = document.createElement('div')
        particle.className = 'particle'

        // 随机位置 - 避免在移动端底部区域生成粒子
        const posX = Math.random() * 100
        const posY = isMobile ? Math.random() * 70 : Math.random() * 100 // 在移动端限制粒子垂直位置

        // 随机大小 - 移动端粒子更小
        const size = isMobile
          ? (Math.random() * 2 + 1)
          : (Math.random() * 5 + 2)

        // 随机动画延迟
        const delay = Math.random() * 5

        // 随机动画持续时间
        const duration = Math.random() * 10 + 15

        particle.style.cssText = `
          left: ${posX}%;
          top: ${posY}%;
          width: ${size}px;
          height: ${size}px;
          animation-delay: ${delay}s;
          animation-duration: ${duration}s;
          opacity: ${isMobile ? (Math.random() * 0.3 + 0.1) : (Math.random() * 0.4 + 0.2)}; // 移动端粒子更透明
        `

        particlesContainer.appendChild(particle)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.home-container {
  width: 100%;
  overflow-x: hidden;
}

.cursor-follower {
  position: fixed;
  width: 20px;
  height: 20px;
  background: rgba(24, 144, 255, 0.2);
  border-radius: 50%;
  pointer-events: none;
  z-index: 9999;
  transition: transform 0.1s ease;
  backdrop-filter: blur(4px);

  &::after {
    content: '';
    position: absolute;
    width: 40px;
    height: 40px;
    border: 2px solid rgba(24, 144, 255, 0.3);
    border-radius: 50%;
    animation: cursorPulse 2s infinite;
  }
}

.background-grid {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    linear-gradient(rgba(24, 144, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(24, 144, 255, 0.05) 1px, transparent 1px);
  background-size: 30px 30px;
  z-index: -1;
  animation: gridMove 20s linear infinite;
}

.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #1890ff, #096dd9);
  z-index: 1001;
  transition: width 0.2s ease;
}

.hero {
  position: relative;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: white;
  padding: 80px 0;
  text-align: center;
  margin-top: 64px;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(circle at 20% 30%, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 80% 70%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  }

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxwYXR0ZXJuIGlkPSJwYXR0ZXJuIiB4PSIwIiB5PSIwIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiIHBhdHRlcm5UcmFuc2Zvcm09InJvdGF0ZSgzMCkiPjxjaXJjbGUgY3g9IjIiIGN5PSIyIiByPSIxIiBmaWxsPSJyZ2JhKDI1NSwgMjU1LCAyNTUsIDAuMSkiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjcGF0dGVybikiLz48L3N2Zz4=');
    opacity: 0.5;
  }

  .hero-background-shapes {
    position: absolute;
    width: 100%;
    height: 100%;
    overflow: hidden;

    .shape {
      position: absolute;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 50%;

      &-1 {
        width: 300px;
        height: 300px;
        top: -150px;
        right: -100px;
        animation: float 6s ease-in-out infinite;
      }

      &-2 {
        width: 200px;
        height: 200px;
        bottom: -100px;
        left: -50px;
        animation: float 8s ease-in-out infinite;
      }

      &-3 {
        width: 150px;
        height: 150px;
        top: 40%;
        right: 15%;
        animation: float 7s ease-in-out infinite;
      }
    }
  }
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero h1 {
  font-size: 48px;
  margin-bottom: 20px;
  font-weight: bold;
}

.hero h2 {
  font-size: 24px;
  font-weight: normal;
  margin-bottom: 40px;
  opacity: 0.9;
}

.hero-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 60px;

  .el-button {
    transition: all 0.3s ease;
    border-radius: 25px;
    padding: 12px 30px;
    font-weight: 500;
    letter-spacing: 0.5px;

    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    }

    &.is-round {
      padding-left: 30px;
      padding-right: 30px;
    }
  }

  .demo-btn {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    font-size: 16px;

    &:hover {
      background: rgba(255, 255, 255, 0.25);
    }

    i {
      margin-right: 8px;
    }
  }
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 60px;
}

.stat-item {
  text-align: center;

  .stat-number {
    font-size: 40px;
    font-weight: bold;
    background: linear-gradient(45deg, #fff, #e6f7ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
    position: relative;
    display: inline-block;

    &::after {
      content: '';
      position: absolute;
      bottom: -5px;
      left: 50%;
      transform: translateX(-50%);
      width: 30px;
      height: 2px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 1px;
    }
  }

  .stat-label {
    font-size: 16px;
    opacity: 0.9;
    font-weight: 500;
  }
}

.section-title {
  text-align: center;
  font-size: 36px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 60px;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    bottom: -16px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, #1890ff, #096dd9);
    border-radius: 2px;
  }
}

.section-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;

  .bg-gradient {
    position: absolute;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, rgba(24, 144, 255, 0.05) 0%, rgba(9, 109, 217, 0.05) 100%);
  }

  .bg-pattern {
    position: absolute;
    width: 100%;
    height: 100%;
    opacity: 0.4;
    background-image: radial-gradient(circle at 1px 1px, #1890ff 1px, transparent 0);
    background-size: 40px 40px;
  }
}

.features {
  padding: 100px 0;
  background: linear-gradient(to bottom, #f8f9fa, #fff);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 40px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
}

.feature-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  max-width: 560px;
  margin: 0 auto;
  width: 100%;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #1890ff, #096dd9);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);

    &::before {
      opacity: 1;
    }

    .feature-icon {
      transform: rotateY(360deg) scale(1.1);
      box-shadow: 0 0 30px rgba(24, 144, 255, 0.3);

      &::before {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(24, 144, 255, 0.2) 0%, transparent 70%);
        animation: iconGlow 2s infinite;
      }
    }
  }

  .feature-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 20px;
    background: #f0f7ff;
    transition: all 0.6s ease;

    i {
      font-size: 36px;
      color: #1890ff;
      transition: color 0.3s ease;
    }
  }

  h3 {
    font-size: 24px;
    color: #262626;
    margin-bottom: 16px;
    font-weight: 600;
  }

  .feature-desc {
    color: #666;
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 30px;
    min-height: 52px;
  }

  .feature-points {
    text-align: left;
    background: #f8f9fa;
    border-radius: 12px;
    padding: 20px;

    .point-item {
      display: flex;
      align-items: flex-start;
      margin-bottom: 12px;
      font-size: 15px;
      color: #595959;

      &:last-child {
        margin-bottom: 0;
      }

      i {
        color: #52c41a;
        margin-right: 10px;
        margin-top: 4px;
        font-size: 16px;
        flex-shrink: 0;
      }

      span {
        line-height: 1.5;
      }
    }
  }
}

.capabilities-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 40px;
}

.capability {
  display: flex;
  align-items: center;
  margin-bottom: 40px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateX(10px);
  }
}

.capability-icon {
  font-size: 36px;
  color: #1890ff;
  margin-right: 20px;
}

.capability-content h3 {
  font-size: 20px;
  margin-bottom: 10px;
}

.plan-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  padding: 0 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.plan-card {
  background: #fff;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  position: relative;
  transition: all 0.3s ease;

  &.recommended {
    transform: scale(1.05);
    border: 2px solid #1890ff;

    &:hover {
      transform: scale(1.05) translateY(-10px);
    }
  }

  &:hover {
    transform: translateY(-10px);
  }

  .recommended-tag {
    position: absolute;
    top: -12px;
    right: 20px;
    background: #1890ff;
    color: white;
    padding: 2px 12px;
    border-radius: 12px;
    font-size: 12px;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 0;
      height: 0;
      border-left: 8px solid transparent;
      border-right: 8px solid transparent;
      border-top: 8px solid #1890ff;
    }
  }
}

.plan-header {
  margin-bottom: 30px;
}

.plan-header h3 {
  font-size: 24px;
  margin-bottom: 15px;
}

.price {
  font-size: 20px;
}

.price .amount {
  font-size: 36px;
  font-weight: bold;
  color: #1890ff;
}

.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 30px;
}

.plan-features li {
  margin: 15px 0;
  color: #666;
}

.plan-features i {
  color: #52c41a;
  margin-right: 8px;
}

.subscribe-btn {
  width: 100%;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
  }
}

@media (max-width: 1024px) {
  .feature-grid {
    gap: 30px;
    padding: 0 30px;
  }
}

@media (max-width: 960px) {
  .feature-grid {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 0 20px;
  }
}

@media (max-width: 768px) {
  .hero {
    height: 100vh;
    margin-top: 0;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
    overflow: hidden;
  }

  .hero-content {
    padding: 0 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    max-width: 100%;
    position: relative;
    z-index: 2;
    padding-top: 60px;
  }

  .hero-background-shapes {
    opacity: 0.4;
  }

  .hero h1 {
    font-size: 28px;
    line-height: 1.3;
    margin-bottom: 16px;
    text-align: center;
    max-width: 100%;
    font-weight: 600;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .hero h2 {
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 30px;
    text-align: center;
    max-width: 90%;
    font-weight: 400;
    opacity: 0.9;
  }

  .hero-buttons {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    margin-bottom: 40px;

    .el-button {
      width: 85%;
      max-width: 280px;
      height: 50px;
      line-height: 50px;
      font-size: 16px;
      font-weight: 500;
      border-radius: 25px;
      margin-bottom: 15px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

      &.is-round {
        padding: 0 30px;
      }

      &:active {
        transform: translateY(2px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
      }
    }

    .demo-btn {
      background: rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.3);

      i {
        margin-right: 8px;
        font-size: 18px;
      }
    }
  }

  .hero-stats {
    width: 90%;
    max-width: 350px;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    padding: 20px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .stat-item {
    text-align: center;

    .stat-number {
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 5px;
      background: linear-gradient(135deg, #ffffff, #e6f7ff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .stat-label {
      font-size: 12px;
      white-space: nowrap;
      opacity: 0.9;
    }
  }

  .particles-container {
    opacity: 0.5;
  }

  .scroll-hint {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    color: white;
    opacity: 0.7;
    animation: bounce 2s infinite;
    z-index: 3;

    i {
      font-size: 24px;
    }
  }

  .feature-grid {
    grid-template-columns: 1fr !important;
    gap: 20px;
    padding: 0 15px;
  }

  .feature-card {
    max-width: 100%;
    width: 100%;
    margin: 0 auto;
    padding: 25px 20px;
  }

  .cursor-follower {
    display: none;
  }
}

@media (max-width: 480px) {
  .hero {
    height: 100vh;
  }

  .hero-content {
    padding-top: 70px;
  }

  .hero h1 {
    font-size: 24px;
    margin-bottom: 14px;
    padding: 0 10px;
  }

  .hero h2 {
    font-size: 14px;
    margin-bottom: 25px;
    padding: 0 15px;
  }

  .hero-buttons {
    margin-bottom: 30px;

    .el-button {
      height: 46px;
      line-height: 46px;
      font-size: 15px;
    }
  }

  .hero-stats {
    width: 85%;
    padding: 15px;
    border-radius: 10px;
  }

  .stat-item {
    .stat-number {
      font-size: 24px;
    }

    .stat-label {
      font-size: 11px;
    }
  }

  .feature-grid {
    gap: 15px;
  }

  .feature-card {
    padding: 20px 15px;
  }
}

.footer {
  background: #001529;
  color: white;
  padding: 60px 0 20px;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-around;
  padding: 0 20px;
}

.footer-section {
  h3 {
    margin-bottom: 20px;
    font-size: 18px;
  }

  p {
    margin: 10px 0;
    color: rgba(255, 255, 255, 0.8);
  }
}

.social-links {
  display: flex;
  gap: 20px;

  a {
    color: white;
    font-size: 24px;
    opacity: 0.8;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-3px);
      opacity: 1;
    }
  }
}

.footer-bottom {
  text-align: center;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
}

.demo-dialog {
  .video-container {
    background: #000;
    border-radius: 8px;
    overflow: hidden;
  }

  .video-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
    background: #1a1a1a;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: #2a2a2a;
    }

    i {
      font-size: 64px;
      margin-bottom: 16px;
      opacity: 0.8;
    }

    p {
      font-size: 16px;
      opacity: 0.6;
    }
  }
}

// 添加滚动动画相关样式
.scroll-animation {
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.6s ease;

  &.animate__animated {
    opacity: 1;
    transform: translateY(0);
  }
}

// 添加动画延迟类
.animate__delay-1s {
  animation-delay: 0.2s;
}

.animate__delay-2s {
  animation-delay: 0.4s;
}

.animate__delay-3s {
  animation-delay: 0.6s;
}

// 优化 Hero 区域动画
.hero-content {
  h1 {
    animation-duration: 1s;
  }

  h2 {
    animation-duration: 1s;
  }

  .hero-buttons {
    animation-duration: 1s;
  }

  .hero-stats {
    animation-duration: 1s;
  }
}

// 优化功能卡片动画
.feature-card {
  &:nth-child(1) { animation-delay: 0.1s; }
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.3s; }
  &:nth-child(4) { animation-delay: 0.4s; }
}

// 优化能力卡片动画
.capability {
  &:nth-child(1) { animation-delay: 0.1s; }
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.3s; }
}

// 优化订阅计划动画
.plan-card {
  &:nth-child(1) { animation-delay: 0.1s; }
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.3s; }
}

@keyframes backgroundMove {
  from {
    background-position: 0 0;
  }
  to {
    background-position: 100% 100%;
  }
}

// 添加滚动提示动画
.scroll-hint {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  opacity: 0.7;
  animation: bounce 2s infinite;
  z-index: 3;

  i {
    font-size: 24px;
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

// 添加新的动画
@keyframes float {
  0% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(5deg);
  }
  100% {
    transform: translateY(0) rotate(0deg);
  }
}

@keyframes iconPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

// 鼠标跟随效果
.cursor-follower {
  position: fixed;
  width: 20px;
  height: 20px;
  background: rgba(24, 144, 255, 0.2);
  border-radius: 50%;
  pointer-events: none;
  z-index: 9999;
  transition: transform 0.1s ease;
  backdrop-filter: blur(4px);

  &::after {
    content: '';
    position: absolute;
    width: 40px;
    height: 40px;
    border: 2px solid rgba(24, 144, 255, 0.3);
    border-radius: 50%;
    animation: cursorPulse 2s infinite;
  }
}

// 背景动态网格
.background-grid {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    linear-gradient(rgba(24, 144, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(24, 144, 255, 0.05) 1px, transparent 1px);
  background-size: 30px 30px;
  z-index: -1;
  animation: gridMove 20s linear infinite;
}

// 滚动进度指示器
.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #1890ff, #096dd9);
  z-index: 1001;
  transition: width 0.2s ease;
}

// 改进卡片悬停效果
.feature-card {
  &:hover {
    .feature-icon {
      transform: rotateY(360deg) scale(1.1);
      box-shadow: 0 0 30px rgba(24, 144, 255, 0.3);

      &::before {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(24, 144, 255, 0.2) 0%, transparent 70%);
        animation: iconGlow 2s infinite;
      }
    }
  }
}

// 改进 Hero 区域视觉效果
.hero {
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 50% 50%, rgba(24, 144, 255, 0.1) 0%, transparent 70%);
    animation: heroGlow 4s ease-in-out infinite;
  }
}

// 添加新的动画
@keyframes cursorPulse {
  0% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.5);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 0.3;
  }
}

@keyframes gridMove {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(30px);
  }
}

@keyframes iconGlow {
  0% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.2);
  }
  100% {
    opacity: 0.5;
    transform: scale(1);
  }
}

@keyframes heroGlow {
  0% {
    opacity: 0.5;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 0.5;
  }
}

.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  pointer-events: none;
  animation: particleFloat 15s infinite linear;
  box-shadow: 0 0 4px rgba(255, 255, 255, 0.4);
}

@keyframes particleFloat {
  0% {
    transform: translateY(0) translateX(0) scale(1);
    opacity: 0;
  }
  10% {
    opacity: 0.8;
  }
  50% {
    transform: translateY(-50px) translateX(50px) scale(1.2);
  }
  90% {
    opacity: 0.8;
  }
  100% {
    transform: translateY(-100px) translateX(100px) scale(1);
    opacity: 0;
  }
}
</style>

