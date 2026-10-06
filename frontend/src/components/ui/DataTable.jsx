import { useState, useEffect } from 'react';
import { Search, Filter, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

export function DataTable({ 
  columns, 
  data, 
  searchPlaceholder = "Search...", 
  loading = false,
  error = null,
  pagination = null,
  onSearchChange = null,
  onPageChange = null,
  searchValue = ""
}) {
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Table Toolbar */}
      <div className="p-4 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="relative max-w-sm w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder={searchPlaceholder}
            value={searchValue}
            onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
          />
        </div>
        <div className="flex space-x-2">
          <button className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto min-h-[300px]">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200 relative">
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-16 text-center">
                  <div className="flex flex-col items-center justify-center text-gray-500">
                    <Loader2 className="h-8 w-8 animate-spin mb-2" />
                    <p>Loading data...</p>
                  </div>
                </td>
              </tr>
            ) : error ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-16 text-center">
                  <div className="text-red-500 bg-red-50 p-4 rounded-md inline-block">
                    <p className="font-medium">Error loading data</p>
                    <p className="text-sm mt-1">{error.message || String(error)}</p>
                  </div>
                </td>
              </tr>
            ) : data && data.length > 0 ? (
              data.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-gray-50">
                  {columns.map((col, colIndex) => (
                    <td
                      key={colIndex}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                    >
                      {col.cell ? col.cell(row) : row[col.accessorKey]}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="px-6 py-16 text-center text-sm text-gray-500">
                  No results found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && (
        <div className="px-6 py-3 border-t border-gray-200 flex items-center justify-between">
          <p className="text-sm text-gray-700">
            Showing page <span className="font-medium">{pagination.page}</span> of{' '}
            <span className="font-medium">{pagination.total_pages}</span> ({' '}
            <span className="font-medium">{pagination.total}</span> total results )
          </p>
          <div className="flex space-x-2">
            <button 
              onClick={() => onPageChange(pagination.page - 1)}
              disabled={pagination.page <= 1 || loading}
              className="p-1 rounded border border-gray-300 text-gray-500 hover:bg-gray-50 disabled:opacity-50">
              <ChevronLeft size={18} />
            </button>
            <button 
              onClick={() => onPageChange(pagination.page + 1)}
              disabled={pagination.page >= pagination.total_pages || loading}
              className="p-1 rounded border border-gray-300 text-gray-500 hover:bg-gray-50 disabled:opacity-50">
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
