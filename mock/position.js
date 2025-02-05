const Mock = require('mockjs')

const List = []
const count = 100

const baseContent = '<p>我们正在寻找...</p>'
const departments = ['技术部', '产品部', '设计部', '运营部', '市场部', '人力资源部']
const cities = ['北京', '上海', '广州', '深圳', '杭州', '成都']

for (let i = 0; i < count; i++) {
  List.push(Mock.mock({
    id: '@increment',
    title: '@ctitle(5, 10)',
    department: '@pick(' + JSON.stringify(departments) + ')',
    type: '@pick(["fulltime", "parttime", "intern"])',
    location: '@pick(' + JSON.stringify(cities) + ')',
    'salaryMin|5-15': 1,
    'salaryMax|15-50': 1,
    salaryUnit: '@pick(["month", "year"])',
    status: '@pick(["active", "paused", "closed"])',
    description: baseContent,
    requirements: baseContent,
    createTime: '@datetime',
    benefits: '@pick(["五险一金", "年终奖", "加班补助", "餐补", "交通补助", "通讯补贴"], 3)',
    'pageViews|2000-5000': 1
  }))
}

module.exports = [
  {
    url: '/position/list',
    type: 'get',
    response: config => {
      const { keyword, type, status, page = 1, limit = 10 } = config.query

      let mockList = List.filter(item => {
        // 关键字过滤
        if (keyword && !item.title.includes(keyword)) return false
        // 类型过滤
        if (type && item.type !== type) return false
        // 状态过滤
        if (status && item.status !== status) return false
        return true
      })

      const pageList = mockList.filter((item, index) => index < limit * page && index >= limit * (page - 1))

      return {
        code: 20000,
        data: {
          total: mockList.length,
          items: pageList
        }
      }
    }
  },

  {
    url: '/position/publish',
    type: 'post',
    response: _ => {
      return {
        code: 20000,
        data: 'success'
      }
    }
  },

  {
    url: /\/position\/\d+/,
    type: 'put',
    response: _ => {
      return {
        code: 20000,
        data: 'success'
      }
    }
  },

  {
    url: /\/position\/\d+\/status/,
    type: 'put',
    response: _ => {
      return {
        code: 20000,
        data: 'success'
      }
    }
  },

  {
    url: /\/position\/\d+/,
    type: 'delete',
    response: _ => {
      return {
        code: 20000,
        data: 'success'
      }
    }
  }
] 