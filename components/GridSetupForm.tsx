import React, { useState } from 'react';

interface GridSetupFormProps {
  onSetupComplete: (config: { plotWidth: number; plotHeight: number; tileWidth: number; tileHeight: number }) => void;
}

export default function GridSetupForm({ onSetupComplete }: GridSetupFormProps) {
  const [plotWidth, setPlotWidth] = useState(100);
  const [plotHeight, setPlotHeight] = useState(80);
  const [tileWidth, setTileWidth] = useState(2);
  const [tileHeight, setTileHeight] = useState(2);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  function validate() {
    const errs: { [key: string]: string } = {};
    if (plotWidth <= 0) errs.plotWidth = 'Plot width must be > 0';
    if (plotHeight <= 0) errs.plotHeight = 'Plot height must be > 0';
    if (tileWidth <= 0) errs.tileWidth = 'Tile width must be > 0';
    if (tileHeight <= 0) errs.tileHeight = 'Tile height must be > 0';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (validate()) {
      onSetupComplete({ plotWidth, plotHeight, tileWidth, tileHeight });
    }
  }

  return (
    <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
      <h2 className="text-2xl font-bold mb-4 text-blue-900">Mall Map Grid Setup</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-semibold text-gray-700">Plot Width (feet):</label>
          <input
            type="number"
            value={plotWidth}
            onChange={e => setPlotWidth(Number(e.target.value))}
            className="border border-gray-300 rounded px-2 py-1 w-full focus:ring-2 focus:ring-blue-400"
            min={1}
            required
          />
          {errors.plotWidth && <p className="text-red-500 text-sm mt-1">{errors.plotWidth}</p>}
        </div>
        <div>
          <label className="block font-semibold text-gray-700">Plot Height (feet):</label>
          <input
            type="number"
            value={plotHeight}
            onChange={e => setPlotHeight(Number(e.target.value))}
            className="border border-gray-300 rounded px-2 py-1 w-full focus:ring-2 focus:ring-blue-400"
            min={1}
            required
          />
          {errors.plotHeight && <p className="text-red-500 text-sm mt-1">{errors.plotHeight}</p>}
        </div>
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block font-semibold text-gray-700">Tile Width (feet):</label>
            <input
              type="number"
              value={tileWidth}
              onChange={e => setTileWidth(Number(e.target.value))}
              className="border border-gray-300 rounded px-2 py-1 w-full focus:ring-2 focus:ring-blue-400"
              min={1}
              required
            />
            {errors.tileWidth && <p className="text-red-500 text-sm mt-1">{errors.tileWidth}</p>}
          </div>
          <div className="flex-1">
            <label className="block font-semibold text-gray-700">Tile Height (feet):</label>
            <input
              type="number"
              value={tileHeight}
              onChange={e => setTileHeight(Number(e.target.value))}
              className="border border-gray-300 rounded px-2 py-1 w-full focus:ring-2 focus:ring-blue-400"
              min={1}
              required
            />
            {errors.tileHeight && <p className="text-red-500 text-sm mt-1">{errors.tileHeight}</p>}
          </div>
        </div>
        <button
          type="submit"
          className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg shadow transition"
        >
          Start Drawing
        </button>
      </form>
    </div>
  );
} 