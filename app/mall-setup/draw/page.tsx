"use client";

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import GridSetupForm from '@/components/GridSetupForm';

const CanvasDrawer = dynamic(() => import('@/components/CanvasDrawer'), {
  ssr: false,
  loading: () => <div className="text-center text-blue-600 mt-10">Loading drawing tool...</div>,
});

export default function MallSetupDraw() {
  const router = useRouter();
  const [setup, setSetup] = useState<null | { plotWidth: number; plotHeight: number; tileWidth: number; tileHeight: number }>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100">
      {/* Back Button */}
      <div className="absolute top-4 left-4 z-10">
        <Button
          variant="outline"
          size="sm"
          onClick={() => router.push('/mall-setup')}
          className="flex items-center gap-2 bg-white/80 backdrop-blur-sm"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Mall Setup
        </Button>
      </div>

      <div className="flex items-center justify-center min-h-screen">
        {!setup ? (
          <GridSetupForm onSetupComplete={setSetup} />
        ) : (
          <CanvasDrawer {...setup} />
        )}
      </div>
    </div>
  );
} 