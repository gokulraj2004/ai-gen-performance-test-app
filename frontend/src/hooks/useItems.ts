/**
 * EXAMPLE HOOK — Demonstrates React Query patterns with CRUD operations.
 * DELETE this file and create your own domain hooks.
 *
 * To remove:
 * 1. Delete this file
 * 2. Remove usage from example pages/components
 * 3. Create your domain hooks (e.g., hooks/usePosts.ts)
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as itemsApi from '../api/items';
import type {
  ItemsQueryParams,
  ItemCreateRequest,
  ItemUpdateRequest,
  TagCreateRequest,
} from '../types';

export function useItems(params: ItemsQueryParams = {}) {
  return useQuery({
    queryKey: ['items', params],
    queryFn: () => itemsApi.getItems(params),
  });
}

export function useItem(itemId: string) {
  return useQuery({
    queryKey: ['items', itemId],
    queryFn: () => itemsApi.getItem(itemId),
    enabled: !!itemId,
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ItemCreateRequest) => itemsApi.createItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });
}

export function useUpdateItem(itemId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ItemUpdateRequest) => itemsApi.updateItem(itemId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      queryClient.invalidateQueries({ queryKey: ['items', itemId] });
    },
  });
}

export function useDeleteItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (itemId: string) => itemsApi.deleteItem(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });
}

export function useTags() {
  return useQuery({
    queryKey: ['tags'],
    queryFn: () => itemsApi.getTags(),
  });
}

export function useCreateTag() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: TagCreateRequest) => itemsApi.createTag(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
  });
}