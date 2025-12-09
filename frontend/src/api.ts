import axios from 'axios'
import type { Item, CartItem, CheckoutResponse, AdminStats, DiscountCode } from './types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      console.error('Cannot connect to backend API at', API_BASE_URL)
    }
    return Promise.reject(error)
  }
)

export const getItems = async (): Promise<Item[]> => {
  const response = await api.get('/api/items/')
  return response.data
}

export const addToCart = async (userId: string, itemId: number, quantity: number): Promise<CartItem> => {
  const response = await api.post(`/api/cart/add?user_id=${userId}`, {
    item_id: itemId,
    quantity,
  })
  return response.data
}

export const getCart = async (userId: string): Promise<CartItem[]> => {
  const response = await api.get(`/api/cart/${userId}`)
  return response.data
}

export const removeFromCart = async (userId: string, itemId: number): Promise<void> => {
  await api.delete(`/api/cart/${userId}/item/${itemId}`)
}

export const checkout = async (userId: string, discountCode?: string): Promise<CheckoutResponse> => {
  const response = await api.post('/api/checkout/', {
    user_id: userId,
    discount_code: discountCode || null,
  })
  return response.data
}

export const getAdminStats = async (): Promise<AdminStats> => {
  const response = await api.get('/api/admin/stats')
  return response.data
}

export const generateDiscountCode = async (): Promise<DiscountCode> => {
  const response = await api.post('/api/admin/discount/generate')
  return response.data
}

export const getAvailableDiscountCodes = async (): Promise<DiscountCode[]> => {
  const response = await api.get('/api/admin/discount/available')
  return response.data
}

