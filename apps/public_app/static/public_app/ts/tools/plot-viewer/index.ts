// Plot Viewer - Barrel Export

import { PlotViewer } from './PlotViewer.js';

export { PlotViewer } from './PlotViewer.js';
export { PlotRenderer } from './renderers.js';
export { ControlsManager } from './controls.js';
export { ExportManager } from './export.js';
export { parseCSV, detectPlots, getDemoData } from './data.js';
export { generateNiceTicks, formatNumber, updateInfoPanel } from './utils.js';
export type { PlotSettings, PlotData, Plot, PlotArea, Scale, Margin } from './types.js';
export { NATURE_COLORS, DEFAULT_SETTINGS } from './types.js';

// Initialize global instance when DOM is ready
let plotViewerInstance: PlotViewer | null = null;

document.addEventListener('DOMContentLoaded', () => {
    plotViewerInstance = new PlotViewer('plotCanvas');

    // Expose global functions for backward compatibility
    (window as any).toggleSettingsPanel = () => {
        plotViewerInstance?.toggleSettings();
    };

    (window as any).updateSetting = (param: string, value: string | number) => {
        plotViewerInstance?.updateSetting(param, value);
    };

    (window as any).resetToNatureDefaults = () => {
        plotViewerInstance?.resetSettings();
    };

    (window as any).downloadPlot = () => {
        plotViewerInstance?.downloadPlot();
    };

    (window as any).loadDemoData = () => {
        plotViewerInstance?.loadDemoData();
    };
});
