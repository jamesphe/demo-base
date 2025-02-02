export default {
  computed: {
    device() {
      return this.$store.state.app.device
    }
  },
  mounted() {
    // 在 iOS 上修复菜单点击无响应的问题
    this.fixBugIniOS()
  },
  methods: {
    fixBugIniOS() {
      const $subMenu = this.$refs.subMenu
      if ($subMenu) {
        const handleMouseleave = $subMenu.handleMouseleave
        const handleMouseenter = $subMenu.handleMouseenter
        $subMenu.handleMouseleave = () => {
          if (this.device === 'mobile') {
            return
          }
          handleMouseleave()
        }
        $subMenu.handleMouseenter = () => {
          if (this.device === 'mobile') {
            return
          }
          handleMouseenter()
        }
      }
    }
  }
}
