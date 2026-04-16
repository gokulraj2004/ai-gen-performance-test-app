/**
 * EXAMPLE TYPES — Demonstrates TypeScript interface patterns.
 * DELETE this file and create your own domain types.
 *
 * To remove:
 * 1. Delete this file
 * 2. Remove re-export from types/index.ts
 * 3. Create your domain type files (e.g., types/posts.ts, types/products.ts)
 */

export interface Tag {
  id: string;
  name: string;
  created_at: string;
}

export interface Item {
  id: string;
  title: string;
  description: string | null;
  tags: Tag[];
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface ItemCreateRequest {
  title: string;
  description?: string;
  tag_names?: string[];
}

export interface ItemUpdateRequest {
  title?: string;
  description?: string;
  tag_names?: string[];
}

export interface TagCreateRequest {
  name: string;
}

export type ItemSortBy = 'title_asc' | 'title_desc' | 'created_at_desc';

export interface ItemsQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  tags?: string[];
  sort_by?: ItemSortBy;
}