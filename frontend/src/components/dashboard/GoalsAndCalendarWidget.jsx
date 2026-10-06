import React, { useState, useEffect } from 'react';
import { 
  Target, Calendar, Plus, CheckCircle2, AlertCircle, 
  Clock, Truck, Package, ArrowUpRight, Loader2 
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardBody } from '../ui/Card';
import { apiClient } from '../../api/client';
import { useAuth } from '../../context/AuthContext';

export function GoalsAndCalendarWidget() {
  const { role } = useAuth();
  const [goals, setGoals] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal state
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [goalForm, setGoalForm] = useState({
    title: '',
    metric: 'TOTAL_REVENUE',
    target_value: '',
    period: 'MONTHLY'
  });

  const canManage = ['Owner', 'Admin', 'Manager'].includes(role);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [goalsRes, eventsRes] = await Promise.all([
        apiClient.get('/goals?page_size=10'),
        apiClient.get('/calendar/events')
      ]);
      setGoals(goalsRes.data?.data || []);
      setEvents(eventsRes.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateGoal = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await apiClient.post('/goals', {
        title: goalForm.title,
        metric: goalForm.metric,
        target_value: parseFloat(goalForm.target_value),
        period: goalForm.period
      });
      setShowGoalModal(false);
      setGoalForm({ title: '', metric: 'TOTAL_REVENUE', target_value: '', period: 'MONTHLY' });
      fetchData();
    } catch (err) {
      alert(err?.response?.data?.detail || 'Failed to create goal');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'ON_TRACK': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'AT_RISK': return 'bg-amber-100 text-amber-800 border-amber-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 my-6">
      {/* ------------------------------------------------------------- */}
      {/* 1. BUSINESS GOALS & OPERATIONAL TARGETS */}
      {/* ------------------------------------------------------------- */}
      <Card>
        <CardHeader
          title="Operational Goals & Targets"
          action={
            canManage && (
              <button
                onClick={() => setShowGoalModal(true)}
                className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                <Plus size={14} /> New Goal
              </button>
            )
          }
        />
        <CardBody className="p-4 space-y-4">
          {loading ? (
            <div className="py-10 text-center text-gray-400 text-xs">
              <Loader2 className="animate-spin inline mr-1" size={16} /> Loading goals...
            </div>
          ) : goals.length === 0 ? (
            <div className="py-10 text-center text-gray-400 text-xs">
              <Target className="mx-auto h-8 w-8 text-gray-300 mb-2" />
              No goals set. Define sales or revenue targets to track live progress.
            </div>
          ) : (
            goals.map((g) => {
              const pct = Math.min(100, Math.max(0, g.progress_percent || 0));
              const isCurrency = ['TOTAL_REVENUE', 'PROFIT'].includes(g.metric);

              return (
                <div key={g.id} className="p-3 bg-gray-50 rounded-lg border border-gray-100">
                  <div className="flex items-center justify-between mb-1.5">
                    <div>
                      <span className="text-xs font-bold text-gray-900">{g.title}</span>
                      <span className="ml-2 text-[10px] text-gray-500 font-mono">({g.period})</span>
                    </div>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${getStatusColor(g.status)}`}>
                      {g.status.replace('_', ' ')}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden my-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        pct >= 100 ? 'bg-emerald-500' : pct >= 70 ? 'bg-blue-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-xs text-gray-600">
                    <span>
                      Current: <strong>{isCurrency ? `$${g.current_value?.toLocaleString()}` : g.current_value}</strong>
                    </span>
                    <span>
                      Target: <strong>{isCurrency ? `$${g.target_value?.toLocaleString()}` : g.target_value}</strong> ({pct.toFixed(0)}%)
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </CardBody>
      </Card>

      {/* ------------------------------------------------------------- */}
      {/* 2. OPERATIONAL CALENDAR & UPCOMING MILESTONES */}
      {/* ------------------------------------------------------------- */}
      <Card>
        <CardHeader
          title="Upcoming Milestones & Schedule"
          action={
            <span className="text-xs text-gray-400">Next 14 Days</span>
          }
        />
        <CardBody className="p-4 space-y-3">
          {loading ? (
            <div className="py-10 text-center text-gray-400 text-xs">
              <Loader2 className="animate-spin inline mr-1" size={16} /> Loading calendar events...
            </div>
          ) : events.length === 0 ? (
            <div className="py-10 text-center text-gray-400 text-xs">
              <Calendar className="mx-auto h-8 w-8 text-gray-300 mb-2" />
              No pending deliveries or fulfillment deadlines on the immediate schedule.
            </div>
          ) : (
            <div className="divide-y divide-gray-100 max-h-72 overflow-y-auto">
              {events.slice(0, 6).map((ev) => (
                <div key={ev.id} className="py-2.5 flex items-start justify-between gap-3 text-xs">
                  <div className="flex items-start gap-2.5">
                    <div className="p-1.5 rounded bg-blue-50 text-blue-600 mt-0.5">
                      {ev.event_type === 'po_delivery' ? (
                        <Truck size={14} />
                      ) : ev.event_type === 'stock_transfer' ? (
                        <Package size={14} />
                      ) : (
                        <Clock size={14} />
                      )}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{ev.title}</p>
                      <p className="text-[11px] text-gray-500 mt-0.5">{ev.description}</p>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="font-mono text-[11px] font-bold text-gray-700 bg-gray-100 px-1.5 py-0.5 rounded">
                      {ev.date}
                    </span>
                    <div className="mt-1">
                      <Link to={ev.link} className="text-[11px] text-blue-600 hover:underline">
                        View →
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* CREATE GOAL MODAL */}
      {showGoalModal && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Set Business Operational Goal</h2>
            <form onSubmit={handleCreateGoal} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Goal Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Q1 Sales Target"
                  value={goalForm.title}
                  onChange={(e) => setGoalForm({ ...goalForm, title: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 uppercase">Metric *</label>
                  <select
                    value={goalForm.metric}
                    onChange={(e) => setGoalForm({ ...goalForm, metric: e.target.value })}
                    className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
                  >
                    <option value="TOTAL_REVENUE">Total Revenue ($)</option>
                    <option value="ORDER_COUNT">Order Volume (#)</option>
                    <option value="CUSTOMER_COUNT">Total Customers (#)</option>
                    <option value="PROFIT">Net Profit ($)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 uppercase">Period</label>
                  <select
                    value={goalForm.period}
                    onChange={(e) => setGoalForm({ ...goalForm, period: e.target.value })}
                    className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
                  >
                    <option value="MONTHLY">Monthly</option>
                    <option value="QUARTERLY">Quarterly</option>
                    <option value="YEARLY">Yearly</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Target Value *</label>
                <input
                  type="number"
                  step="any"
                  required
                  placeholder="e.g. 50000"
                  value={goalForm.target_value}
                  onChange={(e) => setGoalForm({ ...goalForm, target_value: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowGoalModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700"
                >
                  {submitting ? 'Saving...' : 'Set Goal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
