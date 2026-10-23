export type Tab = 'architecture' | 'code' | 'stack' | 'endpoints' | 'queuefy';

export interface Layer {
  name: string;
  description: string;
  color: string;
  glowClass: string;
  icon: string;
  components: string[];
}

export interface StackItem {
  name: string;
  role: string;
  icon: string;
  color: string;
  description: string;
  features: string[];
}

export interface Endpoint {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  description: string;
  layer: string;
}
