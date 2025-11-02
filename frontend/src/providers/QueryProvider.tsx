import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Optimized QueryClient configuration for Next Action Tracker
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Performance optimizations
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors (client errors)
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 2;
      },
      staleTime: 2 * 60 * 1000, // 2 minutes - shorter for real-time feel
      gcTime: 10 * 60 * 1000, // 10 minutes - keep in cache longer
      refetchOnWindowFocus: true, // Refetch when user returns to tab
      refetchOnReconnect: true, // Refetch when network reconnects
      refetchInterval: false, // No automatic polling by default
      
      // Network optimizations
      networkMode: 'online', // Only run queries when online
    },
    mutations: {
      retry: (failureCount, error: any) => {
        // Don't retry mutations on client errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 1; // Only retry once for mutations
      },
      networkMode: 'online',
    },
  },
});

interface QueryProviderProps {
  children: React.ReactNode;
}

export const QueryProvider: React.FC<QueryProviderProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

export default QueryProvider;