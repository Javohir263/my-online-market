/**
 * Typed API endpoint helpers — har biri `api` client orqali.
 */
import { api } from "./client";
import type {
  Cart,
  CategoryNode,
  Brand,
  OrderListItem,
  Paginated,
  ProductDetail,
  ProductListItem,
  User,
} from "@/types/api";

// --- Auth ---
export const authApi = {
  register: (data: {
    email: string;
    password: string;
    password_confirm: string;
    full_name: string;
    language?: string;
  }) => api.post<User>("/auth/register/", data).then((r) => r.data),

  login: (data: { email: string; password: string }) =>
    api.post<User>("/auth/login/", data).then((r) => r.data),

  logout: () => api.post("/auth/logout/").then((r) => r.data),

  me: () => api.get<User>("/auth/me/").then((r) => r.data),
};

// --- Catalog ---
export const catalogApi = {
  categoryTree: () =>
    api.get<CategoryNode[]>("/catalog/categories/").then((r) => r.data),

  brands: () => api.get<Brand[]>("/catalog/brands/").then((r) => r.data),

  products: (params?: Record<string, string | number | boolean>) =>
    api
      .get<Paginated<ProductListItem>>("/catalog/products/", { params })
      .then((r) => r.data),

  product: (slug: string) =>
    api.get<ProductDetail>(`/catalog/products/${slug}/`).then((r) => r.data),

  similar: (slug: string) =>
    api
      .get<ProductListItem[]>(`/catalog/products/${slug}/similar/`)
      .then((r) => r.data),

  featured: () =>
    api
      .get<ProductListItem[]>("/catalog/products/featured/")
      .then((r) => r.data),

  newArrivals: () =>
    api
      .get<ProductListItem[]>("/catalog/products/new-arrivals/")
      .then((r) => r.data),

  bestsellers: () =>
    api
      .get<ProductListItem[]>("/catalog/products/bestsellers/")
      .then((r) => r.data),

  search: (q: string) =>
    api
      .get<Paginated<ProductListItem>>("/catalog/search/", { params: { q } })
      .then((r) => r.data),
};

// --- Cart ---
export const cartApi = {
  get: () => api.get<Cart>("/cart/").then((r) => r.data),

  addItem: (data: {
    product_id: string;
    variant_id?: number;
    quantity?: number;
  }) => api.post("/cart/items/", data).then((r) => r.data),

  updateItem: (id: number, quantity: number) =>
    api.patch(`/cart/items/${id}/`, { quantity }).then((r) => r.data),

  removeItem: (id: number) =>
    api.delete(`/cart/items/${id}/`).then((r) => r.data),

  clear: () => api.delete("/cart/").then((r) => r.data),

  applyCoupon: (code: string) =>
    api.post<Cart>("/cart/coupon/apply/", { code }).then((r) => r.data),

  removeCoupon: () => api.delete<Cart>("/cart/coupon/").then((r) => r.data),
};

// --- Orders ---
export const ordersApi = {
  list: () =>
    api.get<Paginated<OrderListItem>>("/orders/").then((r) => r.data),

  detail: (number: string) =>
    api.get(`/orders/${number}/`).then((r) => r.data),

  checkout: (
    data: { address_id: number; customer_note?: string },
    idempotencyKey?: string,
  ) =>
    api
      .post("/orders/", data, {
        headers: idempotencyKey
          ? { "X-Idempotency-Key": idempotencyKey }
          : undefined,
      })
      .then((r) => r.data),

  cancel: (number: string, reason?: string) =>
    api.post(`/orders/${number}/cancel/`, { reason }).then((r) => r.data),
};

// --- Account ---
export interface Address {
  id: number;
  type: string;
  recipient_name: string;
  recipient_phone: string;
  region: string;
  city: string;
  district: string;
  street: string;
  building: string;
  apartment: string;
  postal_code: string;
  landmark: string;
  is_default: boolean;
  created_at: string;
}

export const accountsApi = {
  profile: () => api.get<User>("/accounts/profile/").then((r) => r.data),

  updateProfile: (data: Partial<User>) =>
    api.patch<User>("/accounts/profile/", data).then((r) => r.data),

  changePassword: (data: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }) => api.put("/accounts/profile/password/", data).then((r) => r.data),

  addresses: () =>
    api.get<Address[]>("/accounts/addresses/").then((r) => r.data),

  createAddress: (data: Partial<Address>) =>
    api.post<Address>("/accounts/addresses/", data).then((r) => r.data),

  updateAddress: (id: number, data: Partial<Address>) =>
    api.patch<Address>(`/accounts/addresses/${id}/`, data).then((r) => r.data),

  deleteAddress: (id: number) =>
    api.delete(`/accounts/addresses/${id}/`).then((r) => r.data),
};
