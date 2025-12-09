export interface Item {
  id: number
  name: string
  price: number
  description?: string
}

export interface CartItem {
  id: number
  item_id: number
  quantity: number
  item: Item
}

export interface CheckoutResponse {
  order_id: number
  total_amount: number
  discount_amount: number
  final_amount: number
  discount_code?: string | null
}

export interface DiscountCode {
  id: number
  code: string
  discount_percentage: number
  is_used: boolean
  created_at: string
}

export interface AdminStats {
  total_items_purchased: number
  total_purchase_amount: number
  discount_codes: DiscountCode[]
  total_discount_amount: number
}

