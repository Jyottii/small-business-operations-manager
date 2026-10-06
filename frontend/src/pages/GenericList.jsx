import { useState } from 'react';
import { DataTable } from '../components/ui/DataTable';
import { useApi } from '../api/hooks';

export default function GenericList({ 
  title, 
  description, 
  columns, 
  primaryAction, 
  onPrimaryAction,
  endpoint 
}) {
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');

  // We append query params to the endpoint
  const queryEndpoint = `${endpoint}?page=${page}&page_size=10${searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : ''}`;
  const { data, loading, error, pagination } = useApi(queryEndpoint);

  const handleSearchChange = (val) => {
    setSearchTerm(val);
    setPage(1); // Reset to page 1 on new search
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          {description && <p className="text-sm text-gray-500">{description}</p>}
        </div>
        {primaryAction && (
          <button 
            onClick={onPrimaryAction}
            className="px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            {primaryAction}
          </button>
        )}
      </div>

      <DataTable 
        columns={columns} 
        data={data || []} 
        loading={loading}
        error={error}
        pagination={pagination}
        searchPlaceholder={`Search ${title.toLowerCase()}...`} 
        searchValue={searchTerm}
        onSearchChange={handleSearchChange}
        onPageChange={handlePageChange}
      />
    </div>
  );
}
