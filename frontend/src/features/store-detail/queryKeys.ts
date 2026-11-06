export const storeDetailKeys = {
  detail: (storeId: string) => ['public', 'store', storeId] as const,
  products: (storeId: string, page: number) =>
    ['public', 'store', storeId, 'products', page] as const,
}
