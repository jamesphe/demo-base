import DescriptionList from './DescriptionList/index.vue'
import DescriptionItem from './DescriptionList/Item.vue'

export {
  DescriptionList,
  DescriptionItem
}

// 提供Vue插件安装方法
export default {
  install(Vue) {
    Vue.component(DescriptionList.name, DescriptionList)
    Vue.component(DescriptionItem.name, DescriptionItem)
  }
} 