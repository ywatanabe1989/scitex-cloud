/**
 * Editor Module Exports
 * Central export point for all editor modules
 */

// History & State Management
export { HistoryManager } from './history/HistoryManager.js';
export { AutoSaveManager } from './io/AutoSave.js';
export type { EditorState } from './io/AutoSave.js';

// Core Canvas Management
export { CanvasManager } from './core/CanvasManager.js';

// Data Management
export { DataTableManager } from './data/DataTableManager.js';

// UI Components
export { PanelLayoutManager } from './ui/PanelLayoutManager.js';
export { PropertiesPanel } from './ui/PropertiesPanel.js';
export { RulersManager } from './ui/RulersManager.js';
export { RulerRenderer, type RulerUnit } from './ui/RulerRenderer.js';
export { ToolbarManager } from './ui/ToolbarManager.js';

// Tools
export { BasicShapes } from './tools/BasicShapes.js';
export { AlignmentTools } from './tools/AlignmentTools.js';
export { SignificanceMarkers } from './tools/SignificanceMarkers.js';
export { ScaleBarTools } from './tools/ScaleBarTools.js';
export { ReferenceGuides } from './tools/ReferenceGuides.js';
export { ScientificAnnotations } from './tools/ScientificAnnotations.js';
export { BasicAnnotations } from './tools/BasicAnnotations.js';
export { AdvancedAnnotations } from './tools/AdvancedAnnotations.js';

// Features
export { ComparisonMode } from './features/ComparisonMode.js';
export { PlotIntegration, type PlotData } from './features/PlotIntegration.js';
export { GalleryManager } from './features/GalleryManager.js';
export { GalleryData } from './features/GalleryData.js';
export { GalleryUI } from './features/GalleryUI.js';

// I/O and File Management
export { FileManager } from './io/FileManager.js';
export { FileExport } from './io/FileExport.js';
export { FileSave } from './io/FileSave.js';
export { VersionControl } from './io/VersionControl.js';
export { VersionComparison } from './io/VersionComparison.js';

// Layout
export { GridManager } from './layout/GridManager.js';
export { GridRenderer } from './layout/GridRenderer.js';
export { RulerDrawer } from './layout/RulerDrawer.js';

// Transform
export { ZoomManager } from './transform/ZoomManager.js';
export { ZoomControls } from './transform/ZoomControls.js';

// Events
export { KeyboardEvents, type KeyboardHandlers } from './events/KeyboardEvents.js';
export { MouseEvents } from './events/MouseEvents.js';

// Utilities
export * from './utils/colors.js';
export * from './utils/geometry.js';
export * from './utils/selection.js';
export * from './utils/validation.js';

// Types
export * from './types.js';
