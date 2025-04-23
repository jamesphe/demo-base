<template>
  <div class="sidebar-container">
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapse"
      :background-color="menuBgColor"
      :text-color="menuTextColor"
      :active-text-color="menuActiveTextColor"
      :unique-opened="false"
      :collapse-transition="false"
      mode="vertical"
    >
      <sidebar-item
        v-for="route in menuItems"
        :key="route.path || route.title"
        :item="route"
        :base-path="route.path"
      />
    </el-menu>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { menuItems } from '@/config/menuConfig'
import SidebarItem from './SidebarItem'
import variables from '@/styles/variables.scss'

// 默认样式值
const defaultVariables = {
  menuBg: '#f5f7fa',
  menuText: '#5a5a5a', 
  menuActiveText: '#1890ff'
}

export default {
  name: 'Sidebar',
  components: { SidebarItem },
  data() {
    return {
      menuItems
    }
  },
  computed: {
    ...mapGetters([
      'sidebar'
    ]),
    activeMenu() {
      const route = this.$route
      const { meta, path } = route
      if (meta.activeMenu) {
        return meta.activeMenu
      }
      return path
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

<style lang="scss" scoped>
.sidebar-container {
  height: 100%;
  .el-menu {
    border: none;
    height: 100%;
    width: 100% !important;
  }
}
</style>
