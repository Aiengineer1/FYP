"use client";

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import GridSetupForm from '@/components/GridSetupForm';

const CanvasDrawer = dynamic(() => import('@/components/CanvasDrawer'), {
  ssr: false,
  loading: () => <div className="text-center text-blue-600 mt-10">Loading drawing tool...</div>,
});

export default function MallSetupDraw() {
  const [setup, setSetup] = useState<null | { plotWidth: number; plotHeight: number; tileWidth: number; tileHeight: number }>(null);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-100">
      {!setup ? (
        <GridSetupForm onSetupComplete={setSetup} />
      ) : (
        <CanvasDrawer {...setup} />
      )}
    </div>
  );
} 