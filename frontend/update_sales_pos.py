import os

content = '''import { useState } from 'react';
import { Search, ShoppingCart, Trash2, Banknote, CreditCard, Loader2 } from 'lucide-react';
import { useApi } from '../../api/hooks';
import { apiClient } from '../../api/client';
import { useNavigate } from 'react-router-dom';

export default function SalesPos() {
  const navigate = useNavigate();
  const [cart, setCart] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const { data: productsData, loading: loadingProducts } = useApi(`/products?search=${encodeURIComponent(searchTerm)}&page_size=24`);
  const products = productsData || [];

  // Assuming a default warehouse for now (normally selected by user context)
  const defaultWarehouseId = "warehouse-123"; 

  const addToCart = (product) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) {
        return prev.map((item) => item.id === product.id ? { ...item, qty: item.qty + 1 } : item);
      }
      return [...prev, { ...product, qty: 1 }];
    });
  };

  const updateQty = (id, delta) => {
    setCart(prev => prev.map(item => {
      if (item.id === id) {
        const newQty = item.qty + delta;
        return newQty > 0 ? { ...item, qty: newQty } : item;
      }
      return item;
    }));
  };

  const removeFromCart = (id) => {
    setCart(prev => prev.filter(item => item.id !== id));
  };

  const subtotal = cart.reduce((sum, item) => sum + (item.selling_price || 0) * item.qty, 0);
  const tax = cart.reduce((sum, item) => sum + ((item.selling_price || 0) * item.qty * ((item.tax_rate || 0)/100)), 0);
  const total = subtotal + tax;

  const handleCompleteSale = async (method) => {
    if (cart.length === 0) return;
    setSubmitting(true);
    setErrorMsg(null);
    
    try {
      const orderPayload = {
        customer_id: null, // Open sale for now, could add customer selector
        employee_id: null,
        notes: `Paid via ${method}`,
        warehouse_id: defaultWarehouseId,
        items: cart.map(item => ({
          product_id: item.id,
          quantity: item.qty,
          discount: 0
        }))
      };

      const order = await apiClient('/orders', { method: 'POST', body: orderPayload });
      
      // Attempt payment
      try {
        await apiClient('/payments', { 
            method: 'POST', 
            body: {
                order_id: order.id,
                amount: order.total,
                payment_method: method,
                transaction_reference: `POS-${Date.now()}`
            }
        });
      } catch (payErr) {
        console.error("Payment failed", payErr);
        // We still redirect to order since it was created
      }

      setCart([]);
      navigate(`/orders/${order.id}`);
      
    } catch (err) {
      setErrorMsg(err.message || String(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col lg:flex-row gap-6">
      {/* Product Section */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {errorMsg && (
          <div className="mb-4 p-4 bg-red-50 text-red-600 rounded-md border border-red-200">
            {errorMsg}
          </div>
        )}
        <div className="mb-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Search products by name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto pb-4 scrollbar-thin">
          {loadingProducts ? (
            <div className="flex justify-center items-center h-64"><Loader2 className="animate-spin text-gray-400 w-8 h-8"/></div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
              {products.map(product => (
                <div 
                  key={product.id} 
                  className={`bg-white rounded-lg border p-4 cursor-pointer hover:shadow-md transition-shadow flex flex-col items-center text-center ${!product.is_active ? 'opacity-50' : ''}`}
                  onClick={() => product.is_active && addToCart(product)}
                >
                  <div className="w-20 h-20 bg-gray-100 rounded-md mb-3 flex items-center justify-center text-gray-400">
                     <ShoppingCart size={24} />
                  </div>
                  <h3 className="text-sm font-medium text-gray-900 mb-1 line-clamp-2">{product.name}</h3>
                  <p className="text-sm font-bold text-blue-600 mt-auto">${(product.selling_price || 0).toFixed(2)}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Cart Section */}
      <div className="w-full lg:w-96 flex flex-col bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden shrink-0">
        <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-bold flex items-center text-gray-800">
            <ShoppingCart className="mr-2" size={20} /> Current Order
          </h2>
          <button className="text-sm text-red-600 hover:text-red-800 font-medium" onClick={() => setCart([])}>Clear</button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
          {cart.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <ShoppingCart size={48} className="mb-4 opacity-20" />
              <p>Your cart is empty</p>
            </div>
          ) : (
            <ul className="space-y-4">
              {cart.map(item => (
                <li key={item.id} className="flex justify-between items-start pb-4 border-b border-gray-100 last:border-0">
                  <div className="flex-1 pr-2">
                    <p className="text-sm font-medium text-gray-900">{item.name}</p>
                    <p className="text-xs text-gray-500">${(item.selling_price||0).toFixed(2)} each</p>
                  </div>
                  <div className="flex flex-col items-end">
                    <p className="text-sm font-bold text-gray-900 mb-2">${((item.selling_price||0) * item.qty).toFixed(2)}</p>
                    <div className="flex items-center space-x-2">
                      <button 
                        onClick={() => updateQty(item.id, -1)}
                        className="w-6 h-6 rounded bg-gray-100 flex items-center justify-center hover:bg-gray-200 text-gray-600"
                      >-</button>
                      <span className="text-sm font-medium w-4 text-center">{item.qty}</span>
                      <button 
                        onClick={() => updateQty(item.id, 1)}
                        className="w-6 h-6 rounded bg-gray-100 flex items-center justify-center hover:bg-gray-200 text-gray-600"
                      >+</button>
                      <button onClick={() => removeFromCart(item.id)} className="ml-2 text-red-500 hover:text-red-700 p-1">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Subtotal</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm text-gray-600">
              <span>Tax Estimated</span>
              <span>${tax.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-lg font-bold text-gray-900 pt-2 border-t border-gray-200">
              <span>Total</span>
              <span>${total.toFixed(2)}</span>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-2 mb-3">
            <button 
                onClick={() => handleCompleteSale('Cash')}
                disabled={cart.length === 0 || submitting}
                className="flex items-center justify-center py-2 px-4 border border-gray-300 rounded-md bg-white hover:bg-gray-50 text-gray-700 font-medium transition-colors disabled:opacity-50">
              <Banknote className="mr-2" size={18} /> Cash
            </button>
            <button 
                onClick={() => handleCompleteSale('Card')}
                disabled={cart.length === 0 || submitting}
                className="flex items-center justify-center py-2 px-4 border border-gray-300 rounded-md bg-white hover:bg-gray-50 text-gray-700 font-medium transition-colors disabled:opacity-50">
              <CreditCard className="mr-2" size={18} /> Card
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
'''
with open('src/pages/Sales/Pos.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
