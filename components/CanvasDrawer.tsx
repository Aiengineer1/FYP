import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Download, ImageIcon, Trash2, HelpCircle, Edit2, XCircle, CornerUpLeft, CornerUpRight } from 'lucide-react';

const CANVAS_WIDTH = 1280;
const CANVAS_HEIGHT = 720;
const OBJECT_COLORS = [
  '#ff6666', '#66b3ff', '#99ff99', '#ffcc99', '#c299ff', '#ffd966', '#ff99c8', '#baffc9'
];

interface MapObject {
  name: string;
  grid_bounds: {
    start_row: number;
    end_row: number;
    start_col: number;
    end_col: number;
  };
  real_world_bounds_ft: {
    x1: number;
    x2: number;
    y1: number;
    y2: number;
  };
  pixel_bounds: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
  area_sq_ft: number;
  color: string;
}

interface CanvasDrawerProps {
  plotWidth: number;
  plotHeight: number;
  tileWidth: number;
  tileHeight: number;
}

export default function CanvasDrawer({ plotWidth, plotHeight, tileWidth, tileHeight }: CanvasDrawerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [objects, setObjects] = useState<MapObject[]>([]);
  const [colorIdx, setColorIdx] = useState(0);
  const [objectName, setObjectName] = useState("");
  const [showHelp, setShowHelp] = useState(false);
  const [nameDialogOpen, setNameDialogOpen] = useState(false);
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPos, setStartPos] = useState<{x: number, y: number} | null>(null);
  const [currentRect, setCurrentRect] = useState<{x1: number, y1: number, x2: number, y2: number} | null>(null);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);
  const [renameIdx, setRenameIdx] = useState<number | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const [history, setHistory] = useState<MapObject[][]>([]);
  const [future, setFuture] = useState<MapObject[][]>([]);

  // Grid calculations - same as Python
  const cols = Math.max(1, Math.floor(plotWidth / tileWidth));
  const rows = Math.max(1, Math.floor(plotHeight / tileHeight));
  const cellW = CANVAS_WIDTH / cols;
  const cellH = CANVAS_HEIGHT / rows;

  // Initialize canvas
  useEffect(() => {
    drawCanvas();
  }, [objects, cols, rows]);

  // Canvas drawing function - equivalent to Python's draw_grid + draw_cell_labels + set_object_cells
  const drawCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    // Draw grid lines (like Python's draw_grid)
    ctx.strokeStyle = '#cccccc';
    ctx.lineWidth = 1;
    
    // Vertical lines
    for (let i = 0; i <= cols; i++) {
      const x = i * cellW;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, CANVAS_HEIGHT);
      ctx.stroke();
    }
    
    // Horizontal lines
    for (let j = 0; j <= rows; j++) {
      const y = j * cellH;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(CANVAS_WIDTH, y);
      ctx.stroke();
    }

    // Draw cell labels (like Python's draw_cell_labels)
    ctx.fillStyle = '#888888';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const x = c * cellW + cellW / 2;
        const y = r * cellH + cellH / 2;
        
        // Check if this cell is covered by any object
        const isCovered = objects.some(obj => 
          r >= obj.grid_bounds.start_row && r <= obj.grid_bounds.end_row &&
          c >= obj.grid_bounds.start_col && c <= obj.grid_bounds.end_col
        );
        
        if (!isCovered) {
          ctx.fillText(`${r + 1},${c + 1}`, x, y);
        }
      }
    }

    // Draw objects (like Python's set_object_cells)
    objects.forEach((obj, idx) => {
      const { start_row, end_row, start_col, end_col } = obj.grid_bounds;
      
      // Fill all covered cells
      ctx.fillStyle = obj.color;
      for (let r = start_row; r <= end_row; r++) {
        for (let c = start_col; c <= end_col; c++) {
          const x = c * cellW;
          const y = r * cellH;
          ctx.fillRect(x, y, cellW, cellH);
        }
      }
      
      // Draw object name in center (like Python)
      const centerX = ((start_col + end_col + 1) / 2) * cellW;
      const centerY = ((start_row + end_row + 1) / 2) * cellH;
      
      ctx.fillStyle = 'black';
      ctx.font = 'bold 14px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(obj.name, centerX, centerY);
      
      // Highlight selected object
      if (idx === selectedIdx) {
        ctx.strokeStyle = '#f59e42';
        ctx.lineWidth = 4;
        const x1 = start_col * cellW;
        const y1 = start_row * cellH;
        const w = (end_col - start_col + 1) * cellW;
        const h = (end_row - start_row + 1) * cellH;
        ctx.strokeRect(x1, y1, w, h);
      }
    });

    // Draw current rectangle being drawn
    if (currentRect && isDrawing) {
      ctx.strokeStyle = 'red';
      ctx.lineWidth = 2;
      const width = currentRect.x2 - currentRect.x1;
      const height = currentRect.y2 - currentRect.y1;
      ctx.strokeRect(currentRect.x1, currentRect.y1, width, height);
    }
  };

  // Mouse event handlers - equivalent to Python's on_mouse_down, on_mouse_drag, on_mouse_up
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    setIsDrawing(true);
    setStartPos({ x, y });
    setCurrentRect({ x1: x, y1: y, x2: x, y2: y });
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDrawing || !startPos) return;
    
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    setCurrentRect({
      x1: Math.min(startPos.x, x),
      y1: Math.min(startPos.y, y),
      x2: Math.max(startPos.x, x),
      y2: Math.max(startPos.y, y)
    });
  }, [isDrawing, startPos]);

  const handleMouseUp = useCallback(() => {
    if (!isDrawing || !currentRect || !startPos) return;
    
    // Snap to grid (like Python)
    const col0 = Math.floor(currentRect.x1 / cellW);
    const col1 = Math.min(cols - 1, Math.floor(currentRect.x2 / cellW));
    const row0 = Math.floor(currentRect.y1 / cellH);
    const row1 = Math.min(rows - 1, Math.floor(currentRect.y2 / cellH));
    
    // Reset drawing state
    setIsDrawing(false);
    setStartPos(null);
    setCurrentRect(null);
    
    // Store pending rectangle data for name dialog
    const pendingObj = {
      row0, row1, col0, col1,
      color: OBJECT_COLORS[colorIdx % OBJECT_COLORS.length]
    };
    
    // Store in a way that name dialog can access
    (window as any).pendingObject = pendingObj;
    setNameDialogOpen(true);
    
  }, [isDrawing, currentRect, startPos, cellW, cellH, cols, rows, colorIdx]);

  // Handle name dialog - equivalent to Python's object creation
  const handleNameDialogClose = (save: boolean) => {
    if (save && objectName.trim() && (window as any).pendingObject) {
      const pending = (window as any).pendingObject;
      
      // Create object exactly like Python
      const newObj: MapObject = {
        name: objectName.trim(),
        grid_bounds: {
          start_row: pending.row0,
          end_row: pending.row1,
          start_col: pending.col0,
          end_col: pending.col1
        },
        real_world_bounds_ft: {
          x1: pending.col0 * tileWidth,
          x2: (pending.col1 + 1) * tileWidth,
          y1: pending.row0 * tileHeight,
          y2: (pending.row1 + 1) * tileHeight
        },
        pixel_bounds: {
          x1: Math.round(pending.col0 * cellW),
          x2: Math.round((pending.col1 + 1) * cellW),
          y1: Math.round(pending.row0 * cellH),
          y2: Math.round((pending.row1 + 1) * cellH)
        },
        area_sq_ft: (pending.row1 - pending.row0 + 1) * (pending.col1 - pending.col0 + 1) * tileWidth * tileHeight,
        color: pending.color
      };
      
      // Add to history for undo
      setHistory(prev => [...prev.slice(-9), objects]);
      setFuture([]);
      
      setObjects(prev => [...prev, newObj]);
      setColorIdx(prev => prev + 1);
    }
    
    setObjectName("");
    setNameDialogOpen(false);
    delete (window as any).pendingObject;
  };

  // Undo/Redo functions
  const handleUndo = () => {
    if (history.length > 0) {
      setFuture(prev => [objects, ...prev.slice(0, 9)]);
      setObjects(history[history.length - 1]);
      setHistory(prev => prev.slice(0, -1));
      setSelectedIdx(null);
    }
  };

  const handleRedo = () => {
    if (future.length > 0) {
      setHistory(prev => [...prev, objects]);
      setObjects(future[0]);
      setFuture(prev => prev.slice(1));
      setSelectedIdx(null);
    }
  };

  // Delete function
  const handleDelete = (idx: number) => {
    setHistory(prev => [...prev, objects]);
    setFuture([]);
    setObjects(objects.filter((_, i) => i !== idx));
    setSelectedIdx(null);
  };

  // Rename functions
  const handleRename = (idx: number) => {
    setRenameIdx(idx);
    setRenameValue(objects[idx].name);
  };

  const handleRenameSave = () => {
    if (renameIdx === null) return;
    const newObjects = [...objects];
    newObjects[renameIdx].name = renameValue;
    setObjects(newObjects);
    setRenameIdx(null);
    setRenameValue('');
  };

  // Export functions - exactly like Python
  const handleExportJSON = () => {
    const data = {
      plot_size_ft: [plotWidth, plotHeight],
      tile_size_ft: [tileWidth, tileHeight],
      tile_size_px: [cellW, cellH],
      canvas_size_px: [CANVAS_WIDTH, CANVAS_HEIGHT],
      grid_rows: rows,
      grid_cols: cols,
      objects: objects,
      notes: 'All calculations and mapping are in feet and pixels. Pixel coordinates are for direct mapping to a camera frame of the same size as the canvas.'
    };
    
    const blob = new Blob([JSON.stringify(data, null, 4)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'floorplan_output_gui.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExportPNG = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const dataURL = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = dataURL;
    a.download = 'floorplan_gui.png';
    a.click();
  };

  const handleClear = () => {
    setObjects([]);
    setHistory([]);
    setFuture([]);
    setSelectedIdx(null);
  };

  const showInstructions = () => {
    setShowHelp(true);
  };

  return (
    <div className="flex w-screen h-screen bg-gray-50">
      {/* Sidebar: Object List */}
      <div className="w-64 bg-white border border-gray-200 rounded-xl shadow-md p-4 flex flex-col gap-2 max-h-full overflow-y-auto">
        <h3 className="text-lg font-semibold mb-2 text-blue-700">Objects</h3>
        {objects.length === 0 && <div className="text-gray-400 text-sm">No objects yet. Drag on canvas to draw.</div>}
        {objects.map((obj, idx) => (
          <div key={idx} className={`flex items-center gap-2 p-2 rounded cursor-pointer ${selectedIdx === idx ? 'bg-blue-50 border border-blue-400' : 'hover:bg-gray-100'}`} onClick={() => setSelectedIdx(idx)}>
            <div className="w-4 h-4 rounded-full" style={{ background: obj.color }} />
            <div className="flex-1">
              <div className="font-semibold text-sm text-blue-900 truncate">{obj.name}</div>
              <div className="text-xs text-gray-500">
                [{obj.grid_bounds.start_row + 1},{obj.grid_bounds.start_col + 1}] - [{obj.grid_bounds.end_row + 1},{obj.grid_bounds.end_col + 1}]
              </div>
              <div className="text-xs text-gray-400">{obj.area_sq_ft} sq ft</div>
            </div>
            <button className="text-blue-600 hover:text-blue-800" onClick={e => { e.stopPropagation(); handleRename(idx); }} title="Rename">
              <Edit2 size={16} />
            </button>
            <button className="text-red-500 hover:text-red-700" onClick={e => { e.stopPropagation(); handleDelete(idx); }} title="Delete">
              <XCircle size={16} />
            </button>
          </div>
        ))}

        {/* Grid Info */}
        <div className="mt-4 p-3 bg-gray-50 rounded text-xs">
          <div className="font-semibold text-gray-700 mb-1">Grid Info:</div>
          <div>{rows} rows × {cols} columns</div>
          <div>Cell: {cellW.toFixed(1)}px × {cellH.toFixed(1)}px</div>
          <div>Tile: {tileWidth}ft × {tileHeight}ft</div>
          <div>Canvas: {CANVAS_WIDTH}×{CANVAS_HEIGHT}px</div>
        </div>
      </div>

      {/* Main content: Top bar + Canvas */}
      <div className="flex-1 flex flex-col h-full">
        <div className="flex gap-4 mb-4 items-center p-4">
          <button onClick={handleExportJSON} className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded shadow flex items-center gap-2">
            <Download size={18} /> JSON
          </button>
          <button onClick={handleExportPNG} className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded shadow flex items-center gap-2">
            <ImageIcon size={18} /> PNG
          </button>
          <button onClick={handleClear} className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded shadow flex items-center gap-2">
            <Trash2 size={18} /> Clear
          </button>
          <button onClick={showInstructions} className="bg-yellow-100 hover:bg-yellow-200 text-yellow-700 px-3 py-1 rounded shadow flex items-center gap-2">
            <HelpCircle size={18} /> Help
          </button>
          <button onClick={handleUndo} className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-1 rounded shadow flex items-center gap-2" disabled={history.length === 0}>
            <CornerUpLeft size={18} /> Undo
          </button>
          <button onClick={handleRedo} className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-1 rounded shadow flex items-center gap-2" disabled={future.length === 0}>
            <CornerUpRight size={18} /> Redo
          </button>
        </div>

        <div className="flex-1 flex justify-center items-center overflow-auto">
          <div className="border rounded-xl overflow-hidden shadow-xl" style={{ width: CANVAS_WIDTH, height: CANVAS_HEIGHT }}>
            <canvas
              ref={canvasRef}
              width={CANVAS_WIDTH}
              height={CANVAS_HEIGHT}
              className="block border border-gray-300 rounded cursor-crosshair"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
            />
          </div>
        </div>
      </div>

      {/* Name dialog */}
      {nameDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h3 className="font-semibold text-lg mb-2">Name This Area</h3>
            <input
              className="border border-gray-300 px-3 py-2 rounded w-full mb-4"
              value={objectName}
              onChange={e => setObjectName(e.target.value)}
              placeholder="e.g., Entrance, Shop, Food Court"
              autoFocus
              onKeyDown={e => e.key === 'Enter' && handleNameDialogClose(true)}
            />
            <div className="flex justify-end gap-2">
              <button 
                className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300" 
                onClick={() => handleNameDialogClose(false)}
              >
                Cancel
              </button>
              <button 
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-blue-300" 
                onClick={() => handleNameDialogClose(true)} 
                disabled={!objectName.trim()}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Rename dialog */}
      {renameIdx !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-80">
            <h3 className="font-semibold text-lg mb-2">Rename Object</h3>
            <input
              className="border border-gray-300 px-3 py-2 rounded w-full mb-4"
              value={renameValue}
              onChange={e => setRenameValue(e.target.value)}
              autoFocus
              onKeyDown={e => e.key === 'Enter' && handleRenameSave()}
            />
            <div className="flex justify-end gap-2">
              <button 
                className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300" 
                onClick={() => { setRenameIdx(null); setRenameValue(''); }}
              >
                Cancel
              </button>
              <button 
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-blue-300" 
                onClick={handleRenameSave} 
                disabled={!renameValue.trim()}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Help dialog */}
      {showHelp && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md">
            <h3 className="font-semibold text-lg mb-3">Instructions</h3>
            <div className="text-sm text-gray-700 space-y-2">
              <p>• Drag mouse on canvas to draw rectangles</p>
              <p>• Enter object name when prompted</p>
              <p>• Click objects in sidebar to select/highlight</p>
              <p>• Use rename/delete buttons in sidebar</p>
              <p>• Export as JSON or PNG when done</p>
              <p>• Canvas size: {CANVAS_WIDTH}×{CANVAS_HEIGHT}px</p>
              <p>• Grid: {rows} rows × {cols} columns</p>
            </div>
            <div className="flex justify-end mt-4">
              <button 
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" 
                onClick={() => setShowHelp(false)}
              >
                Got it!
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}