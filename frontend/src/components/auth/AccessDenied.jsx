import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function AccessDenied({ message }) {
  const { role, currentUser } = useAuth();

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-gray-200 shadow-sm my-8">
      <div className="w-16 h-16 bg-red-50 text-red-600 rounded-full flex items-center justify-center mb-4">
        <ShieldAlert size={32} />
      </div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Restricted</h2>
      <p className="text-gray-600 max-w-md mb-4">
        {message || `Your current role (${role || 'Unknown'}) does not have permission to view or manage this section.`}
      </p>
      <div className="text-xs text-gray-400 bg-gray-50 px-3 py-1.5 rounded-md mb-6">
        Logged in as <span className="font-semibold text-gray-700">{currentUser?.email}</span> ({role})
      </div>
      <Link
        to="/"
        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 transition-colors"
      >
        <ArrowLeft size={16} className="mr-2" />
        Return to Dashboard
      </Link>
    </div>
  );
}
