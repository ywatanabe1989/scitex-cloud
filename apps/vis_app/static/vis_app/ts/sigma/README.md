# Sigma Editor Modularization

## Current Status

### ✅ Completed
- Created module directory structure (`apps/vis_app/static/vis_app/ts/sigma/`)
- Created `types.ts` with all interfaces, type definitions, and constants
- Created `index.ts` for centralized exports
- Created modularization plan

### 🚧 In Progress
- Creating manager module skeletons

### ⏳ Pending
- Extract RulersManager code from sigma-editor.ts
- Extract CanvasManager code from sigma-editor.ts
- Extract DataTableManager code from sigma-editor.ts
- Extract PropertiesManager code from sigma-editor.ts
- Extract UIManager code from sigma-editor.ts
- Refactor main sigma-editor.ts to use modules

## Module Structure

```
apps/vis_app/static/vis_app/ts/sigma/
├── README.md                   # This file
├── MODULARIZATION_PLAN.md      # Detailed plan
├── types.ts                    # ✓ Type definitions and interfaces
├── index.ts                    # ✓ Central export point
├── RulersManager.ts            # ⏳ Ruler rendering and unit management
├── CanvasManager.ts            # ⏳ Fabric.js canvas operations
├── DataTableManager.ts         # ⏳ Data table operations
├── PropertiesManager.ts        # ⏳ Properties panel operations
└── UIManager.ts                # ⏳ UI controls
```

## File Sizes
- **Original**: `sigma-editor.ts` (3,284 lines)
- **Target**: Split into ~6 modules of ~500-600 lines each

## Next Steps

1. **Create Manager Classes**: Each manager will be a class that handles a specific domain
2. **Extract Methods**: Move related methods from SigmaEditor to appropriate managers
3. **Maintain State**: Managers will receive state through constructor or setters
4. **Update Main Class**: SigmaEditor will compose these managers and coordinate between them

## Architecture

The refactored architecture will follow the **Composition pattern**:

```typescript
class SigmaEditor {
    private rulersManager: RulersManager;
    private canvasManager: CanvasManager;
    private dataTableManager: DataTableManager;
    private propertiesManager: PropertiesManager;
    private uiManager: UIManager;

    constructor() {
        // Initialize managers
        this.rulersManager = new RulersManager(/* deps */);
        this.canvasManager = new CanvasManager(/* deps */);
        // ... etc
    }
}
```

## Benefits

1. **Single Responsibility**: Each module has one clear purpose
2. **Maintainability**: Easier to find and fix bugs
3. **Testability**: Can test each manager independently
4. **Collaboration**: Multiple developers can work on different modules
5. **Reusability**: Managers can potentially be reused in other editors

## Guidelines Followed

- ✅ Django Full-Stack Organization Guidelines
- ✅ 1:1:1:1 correspondence (HTML ↔ CSS ↔ TypeScript ↔ Backend)
- ✅ No premature abstraction
- ✅ Self-documenting structure
- ✅ TypeScript hot-reloading enabled (no rebuild needed during development)

## Testing Strategy

After modularization:
1. Test each manager module independently
2. Test integration between managers
3. Verify all existing functionality works
4. Check browser console for errors
5. Test hot-reloading workflow

## Notes

- All modules are automatically compiled by `tsc --watch` in Docker
- Changes are reflected immediately without container restart
- Check compilation logs: `tail -f ./logs/tsc-watch-all.log`
