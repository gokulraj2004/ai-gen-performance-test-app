/**
 * EXAMPLE COMPONENT — Demonstrates card component patterns.
 * DELETE this file and create your own domain components.
 *
 * To remove:
 * 1. Delete the entire components/examples/ directory
 * 2. Remove usage from example pages
 * 3. Create your domain components (e.g., PostCard, ProductCard)
 */
import React from 'react';
import { Link } from 'react-router-dom';
import type { Item } from '../../types';
import { formatDate } from '../../utils/formatDate';

interface ItemCardProps {
  item: Item;
}

export const ItemCard: React.FC<ItemCardProps> = ({ item }) => {
  return (
    <div className="card transition-shadow hover:shadow-md">
      <Link to={`/items/${item.id}`} className="block">
        <h3 className="text-lg font-semibold text-gray-900 hover:text-primary-600">
          {item.title}
        </h3>
      </Link>
      {item.description && (
        <p className="mt-2 line-clamp-2 text-sm text-gray-600">
          {item.description}
        </p>
      )}
      {item.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {item.tags.map((tag) => (
            <span
              key={tag.id}
              className="inline-flex items-center rounded-full bg-primary-50 px-2.5 py-0.5 text-xs font-medium text-primary-700"
            >
              {tag.name}
            </span>
          ))}
        </div>
      )}
      <p className="mt-3 text-xs text-gray-400">
        Created {formatDate(item.created_at)}
      </p>
    </div>
  );
};