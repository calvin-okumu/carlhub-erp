"use client";

import { Suspense } from 'react';

interface SearchParamsWrapperProps {
  children: React.ReactNode;
}

export default function SearchParamsWrapper({ children }: SearchParamsWrapperProps) {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      {children}
    </Suspense>
  );
}