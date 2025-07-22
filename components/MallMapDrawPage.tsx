"use client";

import React, { useRef, useState } from "react";
import { Stage, Layer, Rect, Line, Text } from "react-konva";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField } from "@mui/material";

const CANVAS_WIDTH = 1280;
const CANVAS_HEIGHT = 720;
const GRID_COLOR = "#cccccc";
const OBJECT_COLORS = [
  "#ff6666", "#66b3ff", "#99ff99", "#ffcc99", "#c299ff", "#ffd966", "#ff99c8", "#baffc9"
];

function getGridLines(rows: number, cols: number) {
  const lines = [];
  const cellW = CANVAS_WIDTH / cols;
  const cellH = CANVAS_HEIGHT / rows;
  for (let i = 0; i <= cols; i++) {
    lines.push(
      <Line
        key={`v-${i}`}
        points={[i * cellW, 0, i * cellW, CANVAS_HEIGHT]}
        stroke={GRID_COLOR}
        strokeWidth={1}
      />
    );
  }
  for (let j = 0; j <= rows; j++) {
    lines.push(
      <Line
        key={`h-${j}`}
        points={[0, j * cellH, CANVAS_WIDTH, j * cellH]}
        stroke={GRID_COLOR}
        strokeWidth={1}
      />
    );
  }
  return lines;
}

function FallbackUI({ error }: { error: Error }) {
  return (
    <div style={{ color: 'red', padding: 32, fontWeight: 'bold', fontSize: 20 }}>
      <div>❌ Error in MallMapDrawPage:</div>
      <div>{error.message}</div>
      <div style={{ marginTop: 16, fontSize: 14, color: '#333' }}>
        Please check the browser console for more details.
      </div>
    </div>
  );
}

console.log("MallMapDrawPage component loaded");
export default function MallMapDrawPage() {
  const [step, setStep] = useState<"setup" | "draw">("setup");
  const [plotWidthFt, setPlotWidthFt] = useState(100);
  const [plotHeightFt, setPlotHeightFt] = useState(60);
  const [tileWidthFt, setTileWidthFt] = useState(2);
  const [tileHeightFt, setTileHeightFt] = useState(2);
  const [error, setError] = useState<Error | null>(null);

  // Derived grid
  let cols = 1, rows = 1, cellW = CANVAS_WIDTH, cellH = CANVAS_HEIGHT;
  try {
    cols = Math.max(1, Math.floor(plotWidthFt / tileWidthFt));
    rows = Math.max(1, Math.floor(plotHeightFt / tileHeightFt));
    cellW = CANVAS_WIDTH / cols;
    cellH = CANVAS_HEIGHT / rows;
  } catch (e) {
    setError(e instanceof Error ? e : new Error("Unknown error in grid calculation"));
  }

  // Drawing state
  const [objects, setObjects] = useState<any[]>([]);
  const [drawing, setDrawing] = useState(false);
  const [startPos, setStartPos] = useState<{ x: number; y: number } | null>(null);
  const [currentRect, setCurrentRect] = useState<any>(null);
  const [colorIdx, setColorIdx] = useState(0);

  // Name dialog
  const [nameDialogOpen, setNameDialogOpen] = useState(false);
  const [pendingRect, setPendingRect] = useState<any>(null);
  const [objectName, setObjectName] = useState("");

  // Export
  const stageRef = useRef<any>(null);

  // Debug logs
  console.log("MallMapDrawPage rendered", { step, plotWidthFt, plotHeightFt, tileWidthFt, tileHeightFt, cols, rows, objects });

  // Error boundary
  if (error) {
    console.error("MallMapDrawPage error:", error);
    return <FallbackUI error={error} />;
  }

  // Handle mouse events
  function handleMouseDown(e: any) {
    try {
      if (drawing) return;
      const { x, y } = e.target.getStage().getPointerPosition();
      setStartPos({ x, y });
      setDrawing(true);
      setCurrentRect({
        x1: x,
        y1: y,
        x2: x,
        y2: y,
        color: OBJECT_COLORS[colorIdx % OBJECT_COLORS.length]
      });
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Unknown error in handleMouseDown"));
    }
  }

  function handleMouseMove(e: any) {
    try {
      if (!drawing || !startPos) return;
      const { x, y } = e.target.getStage().getPointerPosition();
      setCurrentRect((rect: any) => rect && { ...rect, x2: x, y2: y });
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Unknown error in handleMouseMove"));
    }
  }

  function handleMouseUp() {
    try {
      if (!drawing || !currentRect) return;
      // Snap to grid
      const x0 = Math.min(currentRect.x1, currentRect.x2);
      const y0 = Math.min(currentRect.y1, currentRect.y2);
      const x1 = Math.max(currentRect.x1, currentRect.x2);
      const y1 = Math.max(currentRect.y1, currentRect.y2);
      const col0 = Math.floor(x0 / cellW);
      const col1 = Math.min(cols - 1, Math.floor(x1 / cellW));
      const row0 = Math.floor(y0 / cellH);
      const row1 = Math.min(rows - 1, Math.floor(y1 / cellH));
      const rect = {
        col0, col1, row0, row1,
        color: currentRect.color,
        pixel: {
          x1: col0 * cellW,
          y1: row0 * cellH,
          x2: (col1 + 1) * cellW,
          y2: (row1 + 1) * cellH
        }
      };
      setPendingRect(rect);
      setNameDialogOpen(true);
      setDrawing(false);
      setCurrentRect(null);
      setStartPos(null);
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Unknown error in handleMouseUp"));
    }
  }

  function handleNameDialogClose(save: boolean) {
    try {
      if (save && pendingRect && objectName.trim()) {
        // Save object
        const obj = {
          name: objectName.trim(),
          grid_bounds: {
            start_row: pendingRect.row0,
            end_row: pendingRect.row1,
            start_col: pendingRect.col0,
            end_col: pendingRect.col1
          },
          real_world_bounds_ft: {
            x1: pendingRect.col0 * tileWidthFt,
            x2: (pendingRect.col1 + 1) * tileWidthFt,
            y1: pendingRect.row0 * tileHeightFt,
            y2: (pendingRect.row1 + 1) * tileHeightFt
          },
          pixel_bounds: {
            x1: Math.round(pendingRect.pixel.x1),
            x2: Math.round(pendingRect.pixel.x2),
            y1: Math.round(pendingRect.pixel.y1),
            y2: Math.round(pendingRect.pixel.y2)
          },
          area_sq_ft:
            (pendingRect.row1 - pendingRect.row0 + 1) *
            (pendingRect.col1 - pendingRect.col0 + 1) *
            tileWidthFt *
            tileHeightFt,
          color: pendingRect.color
        };
        setObjects((objs) => [...objs, obj]);
        setColorIdx((idx) => idx + 1);
      }
      setObjectName("");
      setPendingRect(null);
      setNameDialogOpen(false);
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Unknown error in handleNameDialogClose"));
    }
  }

  function handleExportJSON() {
    try {
      const floorplan = {
        plot_size_ft: [plotWidthFt, plotHeightFt],
        tile_size_ft: [tileWidthFt, tileHeightFt],
        tile_size_px: [cellW, cellH],
        canvas_size_px: [CANVAS_WIDTH, CANVAS_HEIGHT],
        grid_rows: rows,
        grid_cols: cols,
        objects: objects.map((o) => {
          const { color, ...rest } = o;
          return rest;
        }),
        notes:
          "All calculations and mapping are in feet and pixels. Pixel coordinates are for direct mapping to a camera frame of the same size as the canvas."
      };
      const blob = new Blob([JSON.stringify(floorplan, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "floorplan_output_gui.json";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Unknown error in handleExportJSON"));
    }
  }

  function handleExportPNG() {
    try {
      if (stageRef.current) {
        const uri = stageRef.current.toDataURL({ pixelRatio: 2 });
        const a = document.createElement("a");
        a.href = uri;
        a.download = "floorplan_gui.png";
        a.click();
      }
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Unknown error in handleExportPNG"));
    }
  }

  // Step 1: Grid setup form
  if (step === "setup") {
    return (
      <div className="max-w-xl mx-auto mt-10 p-6 bg-white rounded shadow">
        <h2 className="text-2xl font-bold mb-4">Mall Map Grid Setup</h2>
        <div style={{ color: 'blue', marginBottom: 8 }}>DEBUG: Rendering grid setup form</div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (plotWidthFt > 0 && plotHeightFt > 0 && tileWidthFt > 0 && tileHeightFt > 0) {
              setStep("draw");
            }
          }}
          className="space-y-4"
        >
          <div>
            <label className="block font-semibold">Plot Width (feet):</label>
            <input
              type="number"
              value={plotWidthFt}
              onChange={(e) => setPlotWidthFt(Number(e.target.value))}
              className="border rounded px-2 py-1 w-full"
              min={1}
              required
            />
          </div>
          <div>
            <label className="block font-semibold">Plot Height (feet):</label>
            <input
              type="number"
              value={plotHeightFt}
              onChange={(e) => setPlotHeightFt(Number(e.target.value))}
              className="border rounded px-2 py-1 w-full"
              min={1}
              required
            />
          </div>
          <div>
            <label className="block font-semibold">Tile Width (feet):</label>
            <input
              type="number"
              value={tileWidthFt}
              onChange={(e) => setTileWidthFt(Number(e.target.value))}
              className="border rounded px-2 py-1 w-full"
              min={1}
              required
            />
          </div>
          <div>
            <label className="block font-semibold">Tile Height (feet):</label>
            <input
              type="number"
              value={tileHeightFt}
              onChange={(e) => setTileHeightFt(Number(e.target.value))}
              className="border rounded px-2 py-1 w-full"
              min={1}
              required
            />
          </div>
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full"
          >
            Start Drawing
          </button>
        </form>
      </div>
    );
  }

  // Step 2: Drawing canvas
  return (
    <div className="flex flex-col items-center mt-6">
      <h2 className="text-2xl font-bold mb-2">Draw Your Mall Map</h2>
      <div className="mb-2 text-gray-600">
        Canvas size: <b>1280 × 720 px</b> | Grid: <b>{rows} rows × {cols} cols</b> | Tile: <b>{tileWidthFt}ft × {tileHeightFt}ft</b>
      </div>
      <div style={{ color: 'blue', marginBottom: 8 }}>DEBUG: Rendering drawing canvas</div>
      <div className="flex gap-2 mb-4">
        <button
          onClick={handleExportJSON}
          className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        >
          Export as JSON
        </button>
        <button
          onClick={handleExportPNG}
          className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
        >
          Export as PNG
        </button>
      </div>
      <div
        style={{
          border: "2px solid #333",
          background: "#fff",
          width: CANVAS_WIDTH,
          height: CANVAS_HEIGHT,
          marginBottom: 24,
        }}
      >
        <Stage
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          ref={stageRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          style={{ cursor: "crosshair" }}
        >
          <Layer>
            {/* Grid lines */}
            {getGridLines(rows, cols)}
            {/* Cell labels */}
            {Array.from({ length: rows }).map((_, r) =>
              Array.from({ length: cols }).map((_, c) => (
                <Text
                  key={`label-${r}-${c}`}
                  x={c * cellW + cellW / 2 - 16}
                  y={r * cellH + cellH / 2 - 8}
                  text={`${r + 1},${c + 1}`}
                  fontSize={10}
                  fill="#888"
                />
              ))
            )}
            {/* Drawn objects */}
            {objects.map((obj, idx) => (
              <Rect
                key={idx}
                x={obj.pixel_bounds.x1}
                y={obj.pixel_bounds.y1}
                width={obj.pixel_bounds.x2 - obj.pixel_bounds.x1}
                height={obj.pixel_bounds.y2 - obj.pixel_bounds.y1}
                fill={obj.color}
                opacity={0.7}
                stroke="#222"
                strokeWidth={2}
                cornerRadius={4}
              />
            ))}
            {/* Object names */}
            {objects.map((obj, idx) => (
              <Text
                key={`name-${idx}`}
                x={(obj.pixel_bounds.x1 + obj.pixel_bounds.x2) / 2 - 40}
                y={(obj.pixel_bounds.y1 + obj.pixel_bounds.y2) / 2 - 10}
                text={obj.name}
                fontSize={14}
                fontStyle="bold"
                fill="#222"
              />
            ))}
            {/* Current drawing rect */}
            {drawing && currentRect && (
              <Rect
                x={Math.min(currentRect.x1, currentRect.x2)}
                y={Math.min(currentRect.y1, currentRect.y2)}
                width={Math.abs(currentRect.x2 - currentRect.x1)}
                height={Math.abs(currentRect.y2 - currentRect.y1)}
                fill={currentRect.color}
                opacity={0.4}
                stroke="#f00"
                strokeWidth={2}
                dash={[8, 4]}
              />
            )}
          </Layer>
        </Stage>
      </div>
      {/* Name dialog */}
      <Dialog open={nameDialogOpen} onClose={() => handleNameDialogClose(false)}>
        <DialogTitle>Object Name</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Enter object name (e.g., Entrance, Shop, Food Court)"
            fullWidth
            value={objectName}
            onChange={(e) => setObjectName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleNameDialogClose(false)}>Cancel</Button>
          <Button onClick={() => handleNameDialogClose(true)} disabled={!objectName.trim()}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
} 