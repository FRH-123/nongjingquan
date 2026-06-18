"use client";

import { useState, createContext, useContext, ReactNode } from 'react';

interface FilterContextValue {
  villageCode: string | null;
  setVillageCode: (code: string | null) => void;
  groupCode: string | null;
  setGroupCode: (code: string | null) => void;
}

// 创建上下文
const FilterContext = createContext<FilterContextValue | undefined>(undefined);

export function FilterProvider({ children }: { children: ReactNode }) {
  const [villageCode, setVillageCode] = useState<string | null>(null);
  const [groupCode, setGroupCode] = useState<string | null>(null);

  const contextValue: FilterContextValue = {
    villageCode,
    setVillageCode,
    groupCode,
    setGroupCode,
  };

  return (
    <FilterContext.Provider value={contextValue}>
      {children}
    </FilterContext.Provider>
  );
}

export function useFilter() {
  const context = useContext(FilterContext);
  if (context === undefined) {
    throw new Error('useFilter must be used within FilterProvider');
  }
  return context;
}