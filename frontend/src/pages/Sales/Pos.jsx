import { useState } from 'react';
import { 
  Search, ShoppingCart, Trash2, Banknote, CreditCard, Clock, 
  Loader2, User, Warehouse, ScanBarcode, CheckCircle2, AlertCircle 
} from 'lucide-react';
import { useApi } from '../../api/hooks';
import { apiClient } from '../../api/client';
import { useNavigate } from 'react-router-dom';

export default function SalesPos() {
  const navigate = useNavigate();
  const [cart, setCart] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [barcodeInput, setBarcodeInput] = useState('');
  const [scanningBarcode, setScanningBarcode] = useState(false);
  const [scanToast, setScanToast] = useState(null);
  const [selectedCustomer, setSelectedCustomer] = useState('');
  const [selectedWarehouse, setSelectedWarehouse] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const { data: productsData, loading: loadingProducts } = useApi(`/products?search=${encodeURIComponent(searchTerm)}&page_size=36`);
  const { data: customers } = useApi('/customers?page_size=100');
  const { data: warehouses } = useApi('/warehouses?page_size=50');

  const products = productsData || [];
  const activeWarehouse = selectedWarehouse || (warehouses && warehouses[0]?.id) || '';

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

  const handleBarcodeScan = async (e) => {
    e.preventDefault();
    if (!barcodeInput.trim()) return;
    try {
      setScanningBarcode(true);
      const res = await apiClient.get(`/products/barcode/${encodeURIComponent(barcodeInput.trim())}`);
      const product = res.data?.data;
      if (product) {
        addToCart(product);
        setScanToast({ type: 'success', message: `Added to cart: ${product.name} (${product.sku})` });
        setBarcodeInput('');
      }
    } catch (err) {
      setScanToast({ type: 'error', message: `Barcode not found: ${barcodeInput.trim()}` });
    } finally {
      setScanningBarcode(false);
      setTimeout(() => setScanToast(null), 3500);
    }
  };

  const subtotal = cart.reduce((sum, item) => sum + (parseFloat(item.selling_price) || 0) * item.qty, 0);
  const tax = cart.reduce((sum, item) => sum + ((parseFloat(item.selling_price) || 0) * item.qty * ((parseFloat(item.tax_rate) || 0)/100)), 0);
  const total = subtotal + tax;

  const handleCompleteSale = async (paymentOption) => {
    if (cart.length === 0) return;
    setSubmitting(true);
    setErrorMsg(null);
    
    try {
      const orderPayload = {
        customer_id: selectedCustomer || undefined,
        warehouse_id: activeWarehouse,
        notes: `Order created via POS (${paymentOption})`,
        items: cart.map(item => ({
          product_id: item.id,
          quantity: item.qty,
          discount: 0
        }))
      };

      // 1. Create order (atomically deducts stock & checks credit)
      const order = await apiClient('/orders', { method: 'POST', body: orderPayload });
      
      // 2. If immediate payment selected, record payment
      if (paymentOption !== 'Credit') {
        try {
          await apiClient(`/orders/${order.id}/payments`, { 
            method: 'POST', 
            body: {
              amount: order.total,
              payment_method: paymentOption,
              transaction_reference: `POS-${Date.now()}`
            }
          });
        } catch (payErr) {
          console.error("Payment failed", payErr);
        }
      }

      setCart([]);
      navigate(`/orders/${order.id}`);
      
    } catch (err) {
      setErrorMsg(err.message || String(err));
    } finally {
      setSubmitting(false);
    }
  };

  // Find customer credit info if selected
  const currentCust = (customers || []).find(c => c.id === selectedCustomer);

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col lg:flex-row gap-6">
      {/* Product Catalog Section */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {errorMsg && (
          <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-md border border-red-200">
            <strong>Transaction Error:</strong> {errorMsg}
          </div>
        )}

        {/* Barcode Scanner Bar */}
        <form onSubmit={handleBarcodeScan} className="mb-3 flex items-center gap-2">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-blue-600">
              <ScanBarcode className="h-5 w-5" />
            </div>
            <input
              type="text"
              value={barcodeInput}
              onChange={(e) => setBarcodeInput(e.target.value)}
              placeholder="Barcode Scanner: Scan or type product barcode and press Enter..."
              className="block w-full pl-10 pr-24 py-2 border-2 border-blue-200 rounded-lg text-sm bg-blue-50 focus:bg-white focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 placeholder-blue-400 font-mono"
            />
            <button
              type="submit"
              disabled={scanningBarcode || !barcodeInput.trim()}
              className="absolute inset-y-1 right-1 px-3 bg-blue-600 text-white rounded text-xs font-semibold hover:bg-blue-700 disabled:opacity-50"
            >
              {scanningBarcode ? 'Scanning...' : 'Scan / Add'}
            </button>
          </div>
        </form>

        {scanToast && (
          <div className={`mb-3 p-2.5 rounded-lg text-xs font-medium flex items-center gap-2 border ${
            scanToast.type === 'success' 
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200' 
              : 'bg-red-50 text-red-800 border-red-200'
          }`}>
            {scanToast.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
            <span>{scanToast.message}</span>
          </div>
        )}

        {/* Toolbar: Search, Customer, Warehouse */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Search products by name or SKU..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="relative">
            <select
              value={selectedCustomer}
              onChange={(e) => setSelectedCustomer(e.target.value)}
              className="block w-full py-2 px-3 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Walk-in Customer (Cash)</option>
              {(customers || []).map(c => (
                <option key={c.id} value={c.id}>
                  {c.name} {c.credit_limit ? `(Credit: $${c.credit_limit - (c.outstanding_balance || 0)})` : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="relative">
            <select
              value={selectedWarehouse}
              onChange={(e) => setSelectedWarehouse(e.target.value)}
              className="block w-full py-2 px-3 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {(warehouses || []).map(w => (
                <option key={w.id} value={w.id}>{w.name} ({w.code})</option>
              ))}
            </select>
          </div>
        </div>

        {/* Products Grid */}
        <div className="flex-1 overflow-y-auto pb-4 scrollbar-thin">
          {loadingProducts ? (
            <div className="flex justify-center items-center h-64">
              <Loader2 className="animate-spin text-gray-400 w-8 h-8"/>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
              {products.map(product => (
                <div 
                  key={product.id} 
                  className={`bg-white rounded-lg border p-4 cursor-pointer hover:shadow-md transition-shadow flex flex-col items-center text-center ${!product.is_active ? 'opacity-50' : ''}`}
                  onClick={() => product.is_active && addToCart(product)}
                >
                  <div className="w-16 h-16 bg-gray-100 rounded-md mb-2 flex items-center justify-center text-gray-400">
                     <ShoppingCart size={24} />
                  </div>
                  <h3 className="text-sm font-medium text-gray-900 mb-1 line-clamp-2">{product.name}</h3>
                  <span className="text-xs text-gray-500 mb-1">SKU: {product.sku}</span>
                  <p className="text-sm font-bold text-blue-600 mt-auto">${(parseFloat(product.selling_price) || 0).toFixed(2)}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Cart & Checkout Section */}
      <div className="w-full lg:w-96 flex flex-col bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden shrink-0">
        <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h2 className="text-base font-bold flex items-center text-gray-800">
              <ShoppingCart className="mr-2" size={18} /> Current Order
            </h2>
            {currentCust && (
              <p className="text-xs text-gray-500 mt-0.5">Customer: {currentCust.name}</p>
            )}
          </div>
          <button className="text-xs text-red-600 hover:text-red-800 font-medium" onClick={() => setCart([])}>Clear</button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
          {cart.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <ShoppingCart size={40} className="mb-2 opacity-20" />
              <p className="text-sm">Cart is empty</p>
            </div>
          ) : (
            <ul className="space-y-3">
              {cart.map(item => (
                <li key={item.id} className="flex justify-between items-start pb-3 border-b border-gray-100 last:border-0">
                  <div className="flex-1 pr-2">
                    <p className="text-sm font-medium text-gray-900">{item.name}</p>
                    <p className="text-xs text-gray-500">${(parseFloat(item.selling_price)||0).toFixed(2)} each</p>
                  </div>
                  <div className="flex flex-col items-end">
                    <p className="text-sm font-bold text-gray-900 mb-1">${((parseFloat(item.selling_price)||0) * item.qty).toFixed(2)}</p>
                    <div className="flex items-center space-x-2">
                      <button 
                        onClick={() => updateQty(item.id, -1)}
                        className="w-6 h-6 rounded bg-gray-100 flex items-center justify-center hover:bg-gray-200 text-gray-600"
                      >-</button>
                      <span className="text-xs font-semibold w-4 text-center">{item.qty}</span>
                      <button 
                        onClick={() => updateQty(item.id, 1)}
                        className="w-6 h-6 rounded bg-gray-100 flex items-center justify-center hover:bg-gray-200 text-gray-600"
                      >+</button>
                      <button onClick={() => removeFromCart(item.id)} className="ml-1 text-red-500 hover:text-red-700 p-1">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <div className="space-y-1.5 mb-4">
            <div className="flex justify-between text-xs text-gray-600">
              <span>Subtotal</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-xs text-gray-600">
              <span>Tax</span>
              <span>${tax.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-base font-bold text-gray-900 pt-1.5 border-t border-gray-200">
              <span>Total</span>
              <span>${total.toFixed(2)}</span>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="grid grid-cols-2 gap-2">
              <button 
                onClick={() => handleCompleteSale('Cash')}
                disabled={cart.length === 0 || submitting}
                className="flex items-center justify-center py-2 px-3 border border-gray-300 rounded-md bg-white hover:bg-gray-50 text-gray-800 text-xs font-semibold shadow-sm disabled:opacity-50"
              >
                <Banknote className="mr-1.5 text-green-600" size={16} /> Pay Cash
              </button>
              <button 
                onClick={() => handleCompleteSale('Card')}
                disabled={cart.length === 0 || submitting}
                className="flex items-center justify-center py-2 px-3 border border-gray-300 rounded-md bg-white hover:bg-gray-50 text-gray-800 text-xs font-semibold shadow-sm disabled:opacity-50"
              >
                <CreditCard className="mr-1.5 text-blue-600" size={16} /> Pay Card
              </button>
            </div>
            <button 
              onClick={() => handleCompleteSale('Credit')}
              disabled={cart.length === 0 || submitting}
              className="w-full flex items-center justify-center py-2 px-3 border border-yellow-300 rounded-md bg-yellow-50 hover:bg-yellow-100 text-yellow-900 text-xs font-semibold shadow-sm disabled:opacity-50"
            >
              <Clock className="mr-1.5 text-yellow-700" size={16} /> Pay on Credit (Unpaid)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
