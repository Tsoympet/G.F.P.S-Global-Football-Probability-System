import { useEffect, useState } from 'react';

interface QueryState<T> {
  data?: T;
  loading: boolean;
  error?: string;
}

export const useQuery = <T,>(fn: () => Promise<T>, deps: unknown[] = []): QueryState<T> => {
  const [state, setState] = useState<QueryState<T>>({ loading: true });

  useEffect(() => {
    let active = true;
    setState({ loading: true });

    fn()
      .then((data) => {
        if (active) setState({ loading: false, data });
      })
      .catch((error) => {
        if (active) setState({ loading: false, error: error.message });
      });

    return () => {
      active = false;
    };
  }, deps);

  return state;
};
