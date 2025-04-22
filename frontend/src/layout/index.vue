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
import variables from '@/styles/variables.scss'

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
    variables() {
      return variables
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

<style lang="scss">
@import "~@/styles/variables.scss";

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

  .main-container {
    min-height: 100%;
    margin-left: $sideBarWidth;
    position: relative;
    transition: margin-left 0.28s;
  }
}
</style>
