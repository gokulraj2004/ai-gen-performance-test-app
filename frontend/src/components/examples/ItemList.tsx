import { Link } from 'react-router-dom';
import type { Item } from '../../types';

interface ItemListProps {
  items: Item[];
}

export default function ItemList({ items }: ItemListProps) {
  if (!items || items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No items found.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <Link
          key={item.id}
          to={`/items/${item.id}`}
          className="block bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{item.title}</h3>
              {item.description && (
                <p className="text-gray-600 text-sm mt-1 line-clamp-2">
                  {item.description}
                </p>
              )}
            </div>
          </div>
          {item.tags && item.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-3">
              {item.tags.map((tag) => (
                <span
                  key={tag.id}
                  className="px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full text-xs font-medium"
                >
                  {tag.name}
                </span>
              ))}
            </div>
          )}
        </Link>
      ))}
    </div>
  );
}