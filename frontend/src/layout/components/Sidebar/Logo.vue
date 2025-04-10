<template>
  <div class="sidebar-logo-container" :class="{'collapse':collapse}">
    <transition name="sidebarLogoFade">
      <router-link v-if="collapse" key="collapse" class="sidebar-logo-link" to="/">
        <img v-if="logo" :src="logo" class="sidebar-logo">
      </router-link>
      <router-link v-else key="expand" class="sidebar-logo-link" to="/">
        <div class="logo-wrapper">
          <img v-if="logo" :src="logo" class="sidebar-logo">
          <span class="sidebar-title">{{ title }}</span>
        </div>
      </router-link>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'SidebarLogo',
  props: {
    collapse: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      title: 'AI招聘助手',
      logo: require('@/assets/logo.png')
    }
  }
}
</script>

<style lang="scss" scoped>
.sidebar-logo-container {
  position: relative;
  width: 100%;
  height: 50px;
  background: #304156;
  text-align: left;
  overflow: hidden;

  .sidebar-logo-link {
    height: 100%;
    width: 100%;
    display: block;
    overflow: hidden;
    padding: 0 12px;

    .logo-wrapper {
      height: 100%;
      display: flex;
      align-items: center;

      .sidebar-logo {
        width: 28px;
        height: 28px;
        margin-right: 8px;
        vertical-align: middle;
      }

      .sidebar-title {
        display: inline-block;
        color: #fff;
        font-weight: 600;
        font-size: 14px;
        font-family: "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
        white-space: nowrap;
        opacity: 0.95;
      }
    }
  }

  &.collapse {
    .sidebar-logo-link {
      padding: 0;
      .sidebar-logo {
        margin: 11px auto;
        width: 28px;
        height: 28px;
      }
    }
  }
}

.sidebarLogoFade-enter-active,
.sidebarLogoFade-leave-active {
  transition: opacity 0.2s;
}

.sidebarLogoFade-enter,
.sidebarLogoFade-leave-to {
  opacity: 0;
}
</style>
