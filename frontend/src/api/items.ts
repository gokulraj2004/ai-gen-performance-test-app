/**
 * EXAMPLE API CALLS — Demonstrates Axios + React Query patterns.
 * DELETE this file and create your own domain API modules.
 *
 * To remove:
 * 1. Delete this file
 * 2. Remove related hooks (hooks/useItems.ts)
 * 3. Create your domain API files (e.g., api/posts.ts, api/products.ts)
 */
import apiClient from './client';
import type {
  Item,
  ItemCreateRequest,
  ItemUpdateRequest,
  Tag,
  TagCreateRequest,
  ItemsQueryParams,
  PaginatedResponse,
} from '../types';

export async function getItems(
  params: ItemsQueryParams = {},
): Promise<PaginatedResponse<Item>> {
  const queryParams: Record<string, string | number | string[]> = {};

  if (params.page) queryParams.page = params.page;
  if (params.page_size) queryParams.page_size = params.page_size;
  if (params.search) queryParams.search = params.search;
  if (params.sort_by) queryParams.sort_by = params.sort_by;
  if (params.tags && params.tags.length > 0) {
    queryParams.tags = params.tags;
  }

  const response = await apiClient.get<PaginatedResponse<Item>>('/items', {
    params: queryParams,
    paramsSerializer: {
      indexes: null, // serialize arrays as tags=foo&tags=bar (no brackets)
    },
  });
  return response.data;
}

export async function getItem(itemId: string): Promise<Item> {
  const response = await apiClient.get<Item>(`/items/${itemId}`);
  return response.data;
}

export async function createItem(data: ItemCreateRequest): Promise<Item> {
  const response = await apiClient.post<Item>('/items', data);
  return response.data;
}

export async function updateItem(
  itemId: string,
  data: ItemUpdateRequest,
): Promise<Item> {
  const response = await apiClient.put<Item>(`/items/${itemId}`, data);
  return response.data;
}

export async function deleteItem(itemId: string): Promise<void> {
  await apiClient.delete(`/items/${itemId}`);
}

export async function getTags(): Promise<{ tags: Tag[] }> {
  const response = await apiClient.get<{ tags: Tag[] }>('/tags');
  return response.data;
}

export async function createTag(data: TagCreateRequest): Promise<Tag> {
  const response = await apiClient.post<Tag>('/tags', data);
  return response.data;
}