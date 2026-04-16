import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getItem, deleteItem } from '../api/items';

export default function ItemDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: item, isLoading, error } = useQuery({
    queryKey: ['item', id],
    queryFn: () => getItem(id!),
    enabled: !!id,
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteItem(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      navigate('/items');
    },
  });

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      deleteMutation.mutate();
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center py-8 text-gray-500">Loading item...</div>
        </div>
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">Failed to load item. It may not exist.</p>
            <Link
              to="/items"
              className="text-primary-600 hover:text-primary-700"
            >
              ← Back to Items
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-6">
          <Link
            to="/items"
            className="text-primary-600 hover:text-primary-700 text-sm"
          >
            ← Back to Items
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-start mb-4">
            <h1 className="text-2xl font-bold text-gray-900">{item.title}</h1>
            <div className="flex gap-2">
              <button
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>

          {item.description && (
            <p className="text-gray-700 mb-4">{item.description}</p>
          )}

          {item.tags && item.tags.length > 0 && (
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {item.tags.map((tag) => (
                  <span
                    key={tag.id}
                    className="px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-xs font-medium"
                  >
                    {tag.name}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="border-t border-gray-200 pt-4 mt-4 text-sm text-gray-500">
            <p>ID: {item.id}</p>
            {item.created_at && <p>Created: {new Date(item.created_at).toLocaleString()}</p>}
            {item.updated_at && <p>Updated: {new Date(item.updated_at).toLocaleString()}</p>}
          </div>
        </div>

        {deleteMutation.isError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
            Failed to delete item. Please try again.
          </div>
        )}
      </div>
    </div>
  );
}