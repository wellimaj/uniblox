import { useState, useEffect } from 'react'
import { getItems, addToCart, getCart, removeFromCart, checkout, getAdminStats, generateDiscountCode, getAvailableDiscountCodes } from './api'
import type { Item, CartItem, CheckoutResponse, AdminStats, DiscountCode } from './types'

const USER_ID = 'user_123'

function App() {
  const [items, setItems] = useState<Item[]>([])
  const [cart, setCart] = useState<CartItem[]>([])
  const [discountCode, setDiscountCode] = useState('')
  const [appliedDiscount, setAppliedDiscount] = useState<DiscountCode | null>(null)
  const [availableDiscounts, setAvailableDiscounts] = useState<DiscountCode[]>([])
  const [adminStats, setAdminStats] = useState<AdminStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showAdmin, setShowAdmin] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    if (cart.length > 0) {
      loadAvailableDiscounts()
    }
  }, [cart.length])

  const loadData = async () => {
    try {
      setLoading(true)
      setError('')
      const [itemsData, cartData, discounts] = await Promise.all([
        getItems().catch(err => {
          console.error('Failed to load items:', err)
          throw new Error(`Failed to load items: ${err.message || 'Unknown error'}`)
        }),
        getCart(USER_ID).catch(err => {
          console.error('Failed to load cart:', err)
          return []
        }),
        getAvailableDiscountCodes().catch(err => {
          console.error('Failed to load discount codes:', err)
          return []
        })
      ])
      setItems(itemsData)
      setCart(cartData)
      setAvailableDiscounts(discounts)
    } catch (err: any) {
      const errorMessage = err?.message || err?.response?.data?.detail || 'Failed to load data'
      setError(errorMessage)
      console.error('Load data error:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadAvailableDiscounts = async () => {
    try {
      const discounts = await getAvailableDiscountCodes()
      setAvailableDiscounts(discounts)
    } catch (err) {
      console.error('Failed to load discount codes')
    }
  }

  const handleAddToCart = async (itemId: number) => {
    try {
      await addToCart(USER_ID, itemId, 1)
      const updatedCart = await getCart(USER_ID)
      setCart(updatedCart)
      setSuccess('Item added to cart!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to add item to cart')
      setTimeout(() => setError(''), 3000)
    }
  }

  const handleRemoveFromCart = async (itemId: number) => {
    try {
      await removeFromCart(USER_ID, itemId)
      const updatedCart = await getCart(USER_ID)
      setCart(updatedCart)
    } catch (err) {
      setError('Failed to remove item from cart')
      setTimeout(() => setError(''), 3000)
    }
  }

  const handleApplyDiscount = (code: string) => {
    const discount = availableDiscounts.find(d => d.code === code && !d.is_used)
    if (discount) {
      setDiscountCode(code)
      setAppliedDiscount(discount)
      setSuccess(`Discount code "${code}" applied!`)
      setTimeout(() => setSuccess(''), 3000)
    }
  }

  const handleRemoveDiscount = () => {
    setDiscountCode('')
    setAppliedDiscount(null)
  }

  const handleCheckout = async () => {
    if (cart.length === 0) {
      setError('Cart is empty')
      setTimeout(() => setError(''), 3000)
      return
    }

    try {
      const result: CheckoutResponse = await checkout(USER_ID, discountCode || undefined)
      setSuccess(`Order placed successfully! Order ID: ${result.order_id}, Final Amount: $${result.final_amount.toFixed(2)}`)
      setCart([])
      setDiscountCode('')
      setAppliedDiscount(null)
      await loadAvailableDiscounts()
      setTimeout(() => setSuccess(''), 5000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to checkout')
      setTimeout(() => setError(''), 3000)
    }
  }

  const handleLoadAdminStats = async () => {
    try {
      const stats = await getAdminStats()
      setAdminStats(stats)
    } catch (err) {
      setError('Failed to load admin stats')
      setTimeout(() => setError(''), 3000)
    }
  }

  const handleGenerateDiscount = async () => {
    try {
      await generateDiscountCode()
      setSuccess('Discount code generated successfully!')
      await Promise.all([handleLoadAdminStats(), loadAvailableDiscounts()])
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate discount code')
      setTimeout(() => setError(''), 3000)
    }
  }

  const cartTotal = cart.reduce((sum, item) => sum + (item.item.price * item.quantity), 0)
  const discountAmount = appliedDiscount 
    ? cartTotal * (appliedDiscount.discount_percentage / 100)
    : 0
  const finalTotal = cartTotal - discountAmount

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Ecommerce Store</h1>
        <button className="btn btn-primary" onClick={() => setShowAdmin(!showAdmin)}>
          {showAdmin ? 'Hide Admin' : 'Show Admin'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {showAdmin && (
        <div className="admin-section">
          <h2>Admin Panel</h2>
          <button className="btn btn-primary" onClick={handleLoadAdminStats} style={{ marginRight: '10px' }}>
            Load Stats
          </button>
          <button className="btn btn-success" onClick={handleGenerateDiscount}>
            Generate Discount Code
          </button>
          {adminStats && (
            <div>
              <div className="stats-grid">
                <div className="stat-card">
                  <h3>Total Items Purchased</h3>
                  <div className="value">{adminStats.total_items_purchased}</div>
                </div>
                <div className="stat-card">
                  <h3>Total Purchase Amount</h3>
                  <div className="value">${adminStats.total_purchase_amount.toFixed(2)}</div>
                </div>
                <div className="stat-card">
                  <h3>Total Discount Amount</h3>
                  <div className="value">${adminStats.total_discount_amount.toFixed(2)}</div>
                </div>
              </div>
              <div className="discount-codes-list">
                <h3>Discount Codes</h3>
                {adminStats.discount_codes.map((code) => (
                  <div key={code.id} className="discount-code-item">
                    <div>
                      <strong>{code.code}</strong> - {code.discount_percentage}% off
                      {code.is_used ? ' (Used)' : ' (Available)'}
                    </div>
                    <div>{new Date(code.created_at).toLocaleDateString()}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <h2>Products</h2>
      <div className="products-grid">
        {items.map((item) => (
          <div key={item.id} className="product-card">
            <h3>{item.name}</h3>
            <p>{item.description}</p>
            <div className="price">${item.price.toFixed(2)}</div>
            <button className="btn btn-primary" onClick={() => handleAddToCart(item.id)}>
              Add to Cart
            </button>
          </div>
        ))}
      </div>

      <div className="cart-section">
        <h2>Shopping Cart</h2>
        {cart.length === 0 ? (
          <p>Your cart is empty</p>
        ) : (
          <>
            {cart.map((item) => (
              <div key={item.id} className="cart-item">
                <div>
                  <strong>{item.item.name}</strong> - ${item.item.price.toFixed(2)} x {item.quantity}
                </div>
                <button className="btn btn-danger" onClick={() => handleRemoveFromCart(item.item_id)}>
                  Remove
                </button>
              </div>
            ))}
            <div className="cart-summary">
              <div className="cart-total-line">
                <span>Subtotal:</span>
                <span>${cartTotal.toFixed(2)}</span>
              </div>
              {appliedDiscount && (
                <>
                  <div className="cart-discount-line">
                    <span>Discount ({appliedDiscount.code}):</span>
                    <span className="discount-amount">-${discountAmount.toFixed(2)}</span>
                  </div>
                </>
              )}
              <div className="cart-final-total">
                <span>Total:</span>
                <span>${finalTotal.toFixed(2)}</span>
              </div>
            </div>
            <div className="discount-section">
              <label>Available Discount Codes:</label>
              {availableDiscounts.length > 0 ? (
                <div className="discount-codes-available">
                  {availableDiscounts.map((discount) => (
                    <div key={discount.id} className="discount-code-badge">
                      <span className="discount-code-text">{discount.code}</span>
                      <span className="discount-percentage">{discount.discount_percentage}% OFF</span>
                      {discountCode === discount.code ? (
                        <button 
                          className="btn btn-danger btn-small" 
                          onClick={handleRemoveDiscount}
                        >
                          Remove
                        </button>
                      ) : (
                        <button 
                          className="btn btn-success btn-small" 
                          onClick={() => handleApplyDiscount(discount.code)}
                        >
                          Apply
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-discounts">No discount codes available</p>
              )}
              <div className="checkout-button-container">
                <button className="btn btn-success btn-large" onClick={handleCheckout}>
                  Checkout
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default App

