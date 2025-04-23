<template>
  <div :class="{'has-logo':showLogo}" class="sidebar-container">
    <logo v-if="showLogo" :collapse="isCollapse" />
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :background-color="menuBgColor"
        :text-color="menuTextColor"
        :unique-opened="false"
        :active-text-color="menuActiveTextColor"
        :collapse-transition="false"
        mode="vertical"
      >
        <sidebar-item
          v-for="route in routes"
          :key="route.path"
          :item="route"
          :base-path="route.path"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import Logo from './Logo'
import SidebarItem from './SidebarItem'
import variables from '@/styles/variables.scss'

// 默认样式值
const defaultVariables = {
  menuBg: '#f5f7fa',
  menuText: '#5a5a5a', 
  menuActiveText: '#1890ff'
}

export default {
  components: { SidebarItem, Logo },
  computed: {
    ...mapGetters([
      'sidebar',
      'permission_routes'
    ]),
    routes() {
      return this.permission_routes
    },
    activeMenu() {
      const { meta, path } = this.$route
      if (meta.activeMenu) {
        return meta.activeMenu
      }
      return path
    },
    showLogo() {
      return this.$store.state.settings && this.$store.state.settings.sidebarLogo
    },
    menuBgColor() {
      return variables && variables.menuBg ? variables.menuBg : defaultVariables.menuBg
    },
    menuTextColor() {
      return variables && variables.menuText ? variables.menuText : defaultVariables.menuText
    },
    menuActiveTextColor() {
      return variables && variables.menuActiveText ? variables.menuActiveText : defaultVariables.menuActiveText
    },
    variables() {
      return variables || defaultVariables
    },
    isCollapse() {
      return !this.sidebar.opened
    }
  }
}
</script>

<style lang="scss">
@import "~@/styles/variables.scss";

.sidebar-container {
  transition: width 0.28s;
  width: $sideBarWidth !important;
  background-color: $menuBg;
  height: 100%;
  position: fixed;
  font-size: 0px;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1001;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);

  .el-scrollbar {
    height: 100%;
  }

  &.has-logo .el-scrollbar {
    height: calc(100% - 50px);
  }

  .scrollbar-wrapper {
    overflow-x: hidden !important;
  }

  .el-scrollbar__bar.is-vertical {
    right: 0px;
  }

  .el-scrollbar__view {
    height: 100%;
  }

  .is-horizontal {
    display: none;
  }

  a {
    display: inline-block;
    width: 100%;
    overflow: hidden;
  }

  .svg-icon {
    margin-right: 16px;
    color: #5a5a5a;
  }

  .el-menu {
    border: none;
    height: 100%;
    width: 100% !important;
  }

  // 活动菜单项的样式
  .el-menu-item.is-active {
    background-color: $menuHover !important;
    color: $menuActiveText !important;
    border-right: 3px solid $menuActiveText;
  }

  // 菜单项悬停样式
  .el-menu-item:hover, .el-submenu__title:hover {
    background-color: $menuHover !important;
  }

  // 子菜单项样式
  .el-submenu .el-menu-item {
    background-color: $subMenuBg !important;
    &:hover {
      background-color: $subMenuHover !important;
    }
    &.is-active {
      background-color: $menuHover !important;
      border-right: 3px solid $menuActiveText;
    }
  }
}

.sidebar-logo-container {
  position: relative;
  width: 100%;
  height: 50px;
  line-height: 50px;
  text-align: center;
  overflow: hidden;
  transition: background .3s;
  background-color: $menuBg;
  border-bottom: 1px solid #ebeef5;

  .sidebar-logo-link {
    height: 100%;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;

    .sidebar-logo {
      width: 28px;
      height: 28px;
      vertical-align: middle;
      margin-right: 12px;
    }

    .sidebar-title {
      display: inline-block;
      margin: 0;
      font-weight: 600;
      line-height: 50px;
      font-size: 16px;
      font-family: Avenir, Helvetica Neue, Arial, Helvetica, sans-serif;
      vertical-align: middle;
      transition: color .3s;
      color: #1890ff;
    }
  }
}
</style>
