export const storeDetailKeys = {
  detail: (storeId: string) => ['public', 'store', storeId] as const,
}
