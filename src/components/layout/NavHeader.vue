<template>
  <div class="nav-header" :class="{ 'scrolled': isScrolled }">
    <div class="nav-content">
      <div class="nav-left">
        <div class="logo-container">
          <img src="@/assets/logo.png" alt="logo" class="logo">
          <h1 class="brand">AI招聘助手</h1>
        </div>
      </div>

      <!-- 移动端菜单按钮 -->
      <div class="mobile-menu-toggle" @click="toggleMobileMenu">
        <i :class="mobileMenuOpen ? 'el-icon-close' : 'el-icon-menu'" />
      </div>

      <div class="nav-center" :class="{ 'mobile-open': mobileMenuOpen }">
        <a href="#features" class="nav-item" :class="{ 'active': activeSection === 'features' }" @click="closeMobileMenu">
          <i class="el-icon-menu" /> 功能介绍
        </a>
        <a href="#ai-capabilities" class="nav-item" :class="{ 'active': activeSection === 'ai-capabilities' }" @click="closeMobileMenu">
          <i class="el-icon-cpu" /> AI能力
        </a>
        <a href="#pricing" class="nav-item" :class="{ 'active': activeSection === 'pricing' }" @click="closeMobileMenu">
          <i class="el-icon-goods" /> 定价方案
        </a>
        <el-dropdown trigger="hover" class="nav-item">
          <span class="nav-dropdown-link">
            <i class="el-icon-help" /> 帮助与支持 <i class="el-icon-arrow-down el-icon--right" />
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item>
              <i class="el-icon-document" /> 使用文档
            </el-dropdown-item>
            <el-dropdown-item>
              <i class="el-icon-video-camera" /> 视频教程
            </el-dropdown-item>
            <el-dropdown-item>
              <i class="el-icon-chat-dot-round" /> 在线客服
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>

      <div class="nav-right">
        <template v-if="!userLoggedIn">
          <div class="auth-buttons">
            <el-button
              type="text"
              class="login-btn"
              @click="goTo('/login')"
            >
              <i class="el-icon-user" /> 登录
            </el-button>
            <el-button
              type="primary"
              class="trial-btn"
              @click="goTo('/trial-application')"
            >
              <i class="el-icon-data-analysis" /> 免费试用
            </el-button>
          </div>
        </template>
        <template v-else>
          <!-- 通知图标 -->
          <el-popover
            placement="bottom"
            width="320"
            trigger="click"
            popper-class="notification-popover"
          >
            <div class="notification-header">
              <h3>通知</h3>
              <el-button type="text" size="mini" @click="markAllAsRead">全部已读</el-button>
            </div>
            <div class="notification-list">
              <div v-if="notifications.length === 0" class="empty-notifications">
                <i class="el-icon-bell" />
                <p>暂无通知</p>
              </div>
              <div
                v-for="(notification, index) in notifications"
                :key="index"
                class="notification-item"
                :class="{ 'unread': !notification.read }"
              >
                <div class="notification-icon">
                  <i :class="notification.icon" />
                </div>
                <div class="notification-content">
                  <div class="notification-title">{{ notification.title }}</div>
                  <div class="notification-message">{{ notification.message }}</div>
                  <div class="notification-time">{{ notification.time }}</div>
                </div>
              </div>
            </div>
            <div class="notification-footer">
              <el-button type="text" size="small" @click="$router.push('/notifications')">查看全部</el-button>
            </div>
            <el-badge slot="reference" :value="unreadCount" :hidden="unreadCount === 0" class="notice-badge">
              <i class="el-icon-bell notice-icon" />
            </el-badge>
          </el-popover>

          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-profile">
              <el-avatar :size="32" :src="userAvatar">
                {{ userName ? userName.charAt(0).toUpperCase() : 'U' }}
              </el-avatar>
              <span class="username">{{ userName }}</span>
              <i class="el-icon-arrow-down el-icon--right" />
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="dashboard">
                <i class="el-icon-monitor" /> 控制台
              </el-dropdown-item>
              <el-dropdown-item command="profile">
                <i class="el-icon-user" /> 个人中心
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <i class="el-icon-setting" /> 系统设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <i class="el-icon-switch-button" /> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'NavHeader',
  props: {
    isScrolled: {
      type: Boolean,
      default: false
    },
    activeSection: {
      type: String,
      default: ''
    },
    userInfo: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      mobileMenuOpen: false,
      notifications: [
        {
          icon: 'el-icon-message',
          title: '新消息',
          message: '您有一条来自HR的新消息',
          time: '10分钟前',
          read: false
        },
        {
          icon: 'el-icon-document',
          title: '简历解析完成',
          message: '5份简历已完成解析',
          time: '1小时前',
          read: false
        },
        {
          icon: 'el-icon-date',
          title: '面试提醒',
          message: '明天上午10:00有一场面试',
          time: '昨天',
          read: true
        }
      ]
    }
  },
  computed: {
    ...mapGetters({
      userLoggedIn: 'user/userLoggedIn',
      userAvatar: 'user/avatar',
      userName: 'user/name'
    }),
    unreadCount() {
      return this.notifications.filter(n => !n.read).length
    }
  },
  methods: {
    handleCommand(command) {
      console.log('处理导航命令:', command)
      switch (command) {
        case 'dashboard':
          this.handleNavigation('/dashboard')
          break
        case 'profile':
          this.handleNavigation('/profile')
          break
        case 'settings':
          this.handleNavigation('/settings')
          break
        case 'logout':
          this.handleLogout()
          break
      }
    },
    handleNavigation(path) {
      if (!this.$router) {
        console.error('Router is not available')
        return
      }

      Promise.resolve(this.$router.push(path))
        .catch(err => {
          if (err.name !== 'NavigationDuplicated') {
            console.error('导航错误:', err)
          }
        })
    },
    goTo(path) {
      this.handleNavigation(path)
    },
    async handleLogout() {
      try {
        await this.$store.dispatch('user/logout')
        this.handleNavigation('/login')
      } catch (error) {
        console.error('登出错误:', error)
      }
    },
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen
      if (this.mobileMenuOpen) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    },
    closeMobileMenu() {
      this.mobileMenuOpen = false
      document.body.style.overflow = ''
    },
    markAllAsRead() {
      this.notifications.forEach(notification => {
        notification.read = true
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.nav-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0);
  z-index: 1000;
  transition: all 0.3s ease;

  &.scrolled {
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;

  .logo {
    height: 36px;
    width: auto;
    transition: transform 0.3s ease;

    &:hover {
      transform: scale(1.1);
    }
  }

  .brand {
    font-size: 24px;
    background: linear-gradient(45deg, #1890ff, #096dd9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    transition: all 0.3s ease;

    &:hover {
      transform: translateX(5px);
    }
  }
}

.nav-left {
  display: flex;
  align-items: center;
}

.nav-center {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 15px;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;

  i {
    font-size: 18px;
  }

  &:hover, &.active {
    color: #1890ff;
    background: rgba(24, 144, 255, 0.1);
  }
}

.nav-dropdown-link {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    background: rgba(0, 0, 0, 0.05);
  }

  .username {
    font-size: 14px;
    color: #333;
  }
}

.notice-badge {
  margin-left: 16px;
  margin-right: 16px;

  .notice-icon {
    font-size: 20px;
    color: #666;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      color: #1890ff;
    }
  }
}

// 移动端菜单按钮
.mobile-menu-toggle {
  display: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  transition: all 0.3s ease;

  &:hover {
    color: #1890ff;
  }
}

// 通知样式
.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #eee;

  h3 {
    margin: 0;
    font-size: 16px;
  }
}

.notification-list {
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  padding: 12px 15px;
  border-bottom: 1px solid #f5f5f5;
  transition: all 0.3s ease;

  &:hover {
    background-color: #f9f9f9;
  }

  &.unread {
    background-color: rgba(24, 144, 255, 0.05);

    &::before {
      content: '';
      display: block;
      width: 6px;
      height: 6px;
      background-color: #1890ff;
      border-radius: 50%;
      position: absolute;
      left: 10px;
      margin-top: 8px;
    }
  }
}

.notification-icon {
  margin-right: 12px;

  i {
    font-size: 20px;
    color: #1890ff;
    background: rgba(24, 144, 255, 0.1);
    padding: 8px;
    border-radius: 50%;
  }
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.notification-message {
  color: #666;
  font-size: 13px;
  margin-bottom: 4px;
}

.notification-time {
  color: #999;
  font-size: 12px;
}

.notification-footer {
  padding: 10px 15px;
  text-align: center;
  border-top: 1px solid #eee;
}

.empty-notifications {
  padding: 30px 0;
  text-align: center;
  color: #999;

  i {
    font-size: 40px;
    margin-bottom: 10px;
  }
}

@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: block;
    order: 3;
  }

  .nav-content {
    position: relative;
  }

  .nav-center {
    position: fixed;
    top: 64px;
    left: 0;
    right: 0;
    bottom: 0;
    background: white;
    flex-direction: column;
    justify-content: flex-start;
    padding: 20px;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    z-index: 999;
    overflow-y: auto;

    &.mobile-open {
      transform: translateX(0);
    }

    .nav-item {
      width: 100%;
      padding: 15px;
      border-bottom: 1px solid #f5f5f5;
      justify-content: flex-start;
    }

    .el-dropdown {
      width: 100%;
    }
  }

  .nav-right {
    margin-right: 20px;
  }

  .username {
    display: none;
  }

  .auth-buttons {
    gap: 5px;
  }

  .login-btn {
    padding: 6px 10px;
  }

  .trial-btn {
    padding: 6px 12px;
    font-size: 13px;
  }

  .logo-container {
    .logo {
      height: 30px;
    }

    .brand {
      font-size: 18px;
      display: block;
    }
  }

  .notice-badge {
    margin-left: 8px;
    margin-right: 8px;
  }
}

@media (max-width: 480px) {
  .nav-header {
    height: 60px;
  }

  .nav-center {
    top: 60px;
  }

  .logo-container {
    gap: 8px;
    display: flex;
    align-items: center;

    .logo {
      height: 26px;
    }

    .brand {
      font-size: 16px;
      white-space: nowrap;
      display: block;
    }
  }

  .auth-buttons {
    .login-btn {
      padding: 4px 6px;
      font-size: 12px;
    }

    .trial-btn {
      padding: 4px 8px;
      font-size: 12px;
    }
  }

  .mobile-menu-toggle {
    font-size: 20px;
    margin-left: 5px;
  }

  .notice-icon {
    font-size: 18px;
  }

  .user-profile .el-avatar {
    width: 28px;
    height: 28px;
  }

  .nav-right {
    margin-right: 10px;
  }
}

@media (max-width: 360px) {
  .logo-container {
    .brand {
      font-size: 14px;
    }
  }

  .auth-buttons {
    gap: 4px;

    .login-btn {
      padding: 3px 5px;
    }

    .trial-btn {
      padding: 3px 6px;
    }
  }
}

/* 登录和试用按钮样式 */
.auth-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.login-btn {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  padding: 8px 15px;
  transition: all 0.3s;

  &:hover {
    color: #409EFF;
    background: rgba(64, 158, 255, 0.08);
    border-radius: 4px;
  }

  i {
    margin-right: 4px;
  }
}

.trial-btn {
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 20px;
  background: linear-gradient(135deg, #409EFF 0%, #53a8ff 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(64, 158, 255, 0.4);
  }

  i {
    margin-right: 4px;
  }
}
</style>
