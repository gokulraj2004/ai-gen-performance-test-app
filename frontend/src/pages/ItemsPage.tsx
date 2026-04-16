import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getItems } from '../api/items';
import ItemList from '../components/examples/ItemList';

export default function ItemsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['items', page, search],
    queryFn: () => getItems({ page, page_size: 10, search: search || undefined }),
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Items</h1>
          <Link
            to="/"
            className="text-primary-600 hover:text-primary-700 text-sm"
          >
            ← Back to Home
          </Link>
        </div>

        <div className="mb-6">
          <input
            type="text"
            placeholder="Search items..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {isLoading && (
          <div className="text-center py-8 text-gray-500">Loading items...</div>
        )}

        {error && (
          <div className="text-center py-8 text-red-600">
            Failed to load items. Please try again.
          </div>
        )}

        {data && (
          <>
            <ItemList items={data.items} />

            <div className="flex justify-between items-center mt-6">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-4 py-2 bg-white border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {page} of {Math.ceil((data.total || 0) / (data.page_size || 10))}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!data.items || data.items.length < (data.page_size || 10)}
                className="px-4 py-2 bg-white border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}