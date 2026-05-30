/**
 * API model types — backend DRF serializerlariga mos.
 */

export type Language = "uz" | "ru" | "en";
export type UserRole = "customer" | "staff" | "admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone: string;
  language: Language;
  role: UserRole;
  is_email_verified: boolean;
  is_phone_verified: boolean;
  created_at: string;
}

export interface CategoryNode {
  id: number;
  slug: string;
  name: string;
  icon: string;
  image: string | null;
  products_count: number;
  order: number;
  children: CategoryNode[];
}

export interface Brand {
  id: number;
  slug: string;
  name: string;
  description: string;
  logo: string | null;
  is_active: boolean;
}

export interface ProductTag {
  id: number;
  slug: string;
  name: string;
  color: string;
}

export interface ProductImage {
  id: number;
  image: string;
  alt_text: string;
  order: number;
  is_primary: boolean;
}

export interface ProductVariant {
  id: number;
  sku: string;
  color: string;
  size: string;
  additional_price: string;
  final_price: string;
  stock_quantity: number;
  image: string | null;
  is_active: boolean;
}

export interface ProductAttribute {
  id: number;
  name: string;
  value: string;
  order: number;
}

export interface ProductListItem {
  id: string;
  slug: string;
  sku: string;
  name: string;
  short_description: string;
  currency: string;
  base_price: string;
  sale_price: string | null;
  current_price: string;
  has_discount: boolean;
  discount_percentage: number;
  stock_quantity: number;
  is_in_stock: boolean;
  ratings_avg: string;
  ratings_count: number;
  is_featured: boolean;
  is_new: boolean;
  is_bestseller: boolean;
  brand: { id: number; slug: string; name: string } | null;
  category: { id: number; slug: string; name: string };
  primary_image: string | null;
}

export interface ProductDetail extends ProductListItem {
  description: string;
  views_count: number;
  images: ProductImage[];
  variants: ProductVariant[];
  attributes: ProductAttribute[];
  tags: ProductTag[];
}

export interface CartItem {
  id: number;
  product: ProductListItem;
  variant: ProductVariant | null;
  quantity: number;
  price_snapshot: string;
  line_total: string;
  available_stock: number;
  created_at: string;
}

export interface Cart {
  id: number;
  items: CartItem[];
  items_count: number;
  subtotal: string;
  discount_amount: string;
  total: string;
  coupon: { code: string; type: string; value: string } | null;
  updated_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type OrderStatus =
  | "pending"
  | "confirmed"
  | "shipped"
  | "delivered"
  | "cancelled";

export interface OrderListItem {
  id: string;
  number: string;
  status: OrderStatus;
  currency: string;
  total: string;
  items_count: number;
  created_at: string;
}
