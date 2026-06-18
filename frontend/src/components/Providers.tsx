"use client";

import { FilterProvider } from "@/hooks/useFilter";
import { ReactNode } from "react";

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <FilterProvider>
      {children}
    </FilterProvider>
  );
}