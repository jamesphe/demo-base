import request from '@/utils/request'

// 获取实训室列表
export function getTrainingRooms(query) {
  return request({
    url: '/api/training-rooms',
    method: 'get',
    params: query
  })
}

// 模拟数据 - 开发时使用
const mockDetail = {
  id: 1,
  roomCode: 'TR001',
  name: '计算机实训室',
  status: 'available',
  baseName: '信息技术实训基地',
  physicalRoomNo: 'A-301',
  physicalRoomName: '计算机实验室',
  managerId: '10001',
  establishDate: '2023-01-01',
  cooperativeCompany: '华为技术有限公司',
  buildingArea: 120,
  usableArea: 100,
  capacity: 50,
  deviceCount: 51,
  weeklyClassHours: 40,
  facilities: '电脑50台、投影仪1台、空调2台',
  remark: '主要用于计算机基础课程实训'
}

// 获取单个实训室详情
export function getTrainingRoom(id) {
  // 开发环境使用模拟数据
  if (process.env.NODE_ENV === 'development') {
    return Promise.resolve({
      code: 20000,
      data: mockDetail
    })
  }

  return request({
    url: `/api/training-rooms/${id}`,
    method: 'get'
  })
}

// 创建实训室
export function createTrainingRoom(data) {
  return request({
    url: '/api/training-rooms',
    method: 'post',
    data
  })
}

// 更新实训室
export function updateTrainingRoom(id, data) {
  return request({
    url: `/api/training-rooms/${id}`,
    method: 'put',
    data
  })
}

// 删除实训室
export function deleteTrainingRoom(id) {
  return request({
    url: `/api/training-rooms/${id}`,
    method: 'delete'
  })
}
