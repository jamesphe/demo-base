<template>
  <div :class="classObj" class="app-wrapper">
    <!-- 左侧导航栏 -->
    <sidebar class="sidebar-container" />

    <div class="main-container">
      <!-- 顶部导航栏 -->
      <navbar />

      <!-- 主要内容区域 -->
      <app-main />
    </div>
  </div>
</template>

<script>
import { Navbar, Sidebar, AppMain } from './components'
import { mapState } from 'vuex'

export default {
  name: 'Layout',
  components: {
    Navbar,
    Sidebar,
    AppMain
  },
  computed: {
    ...mapState({
      sidebar: state => state.app.sidebar
    }),
    classObj() {
      return {
        hideSidebar: !this.sidebar.opened,
        openSidebar: this.sidebar.opened,
        withoutAnimation: this.sidebar.withoutAnimation
      }
    },
    debugInfo() {
      return {
        currentRoute: this.$route.path,
        routeName: this.$route.name,
        hasNavHeader: !!this.$options.components.NavHeader
      }
    }
  },
  created() {
    console.log('Layout组件创建:', {
      route: this.$route,
      components: this.$options.components
    })
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll, {
      passive: true
    })
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.handleScroll)
  }
}
</script>

<style lang="scss" scoped>
.app-wrapper {
  position: relative;
  height: 100%;
  width: 100%;

  &:after {
    content: "";
    display: table;
    clear: both;
  }

  &.hideSidebar {
    .sidebar-container {
      width: 54px !important;
    }
    .main-container {
      margin-left: 54px;
    }
  }

  .sidebar-container {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 210px;
    height: 100%;
    background: #304156;
    z-index: 1001;
    transition: width 0.28s;
    overflow: hidden;
  }

  .main-container {
    min-height: 100%;
    margin-left: 210px;
    position: relative;
    transition: margin-left 0.28s;
  }
}
</style>
