import { useState } from 'react';

export function useLoading() {
  const [isLoading, setIsLoading] = useState(false);

  return {
    isLoading,
    setLoading: setIsLoading,
  };
}
