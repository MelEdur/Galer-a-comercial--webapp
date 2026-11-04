export const productDetailKeys = {
  detail: (productId: string) => ['public', 'product', productId] as const,
  similar: (productId: string) =>
    ['public', 'product', productId, 'similar'] as const,
}
