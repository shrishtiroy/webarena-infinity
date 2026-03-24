# Google Sheets - Spreadsheet Editor

## Summary
A browser-based spreadsheet application modeled after Google Sheets. Supports a 100-row by 26-column (A-Z) grid per sheet, formula evaluation with a dependency graph, cell formatting (bold, italic, colors, borders, merge), charting (bar, line, pie, scatter), multi-sheet workbook management, sorting, filtering, conditional formatting, named ranges, data validation, find/replace, and undo/redo. Single-user, no collaboration features. The app opens with 3 pre-populated sheets: Sales, Employees, and Inventory.

## Main Sections / Pages
This is a single-page application with one main view containing:
1. **Menu Bar** - File, Edit, View, Insert, Format, Data, Tools menus
2. **Toolbar Ribbon** - Quick-access buttons for formatting and common actions
3. **Formula Bar** - Cell address label (left) and formula/value input (right)
4. **Grid Area** - The main spreadsheet grid with column/row headers
5. **Charts Overlay** - Floating chart containers rendered over the grid
6. **Sheet Tabs Bar** - Bottom tab bar for switching/managing sheets

## Complete List of Implemented Features

### Grid Engine
- 100 rows x 26 columns (A-Z) per sheet
- Virtual/windowed rendering (only visible rows + buffer rendered)
- Click to select single cell
- Shift-click to extend selection range
- Ctrl/Cmd-click for non-contiguous selection
- Click column header to select entire column
- Click row header to select entire row
- Click corner header to select all cells
- Column resize via drag on column header border
- Row resize via drag on row header border
- Column auto-fit via double-click on column header border
- Freeze rows and columns via View menu

### Editing
- Inline cell editor on double-click or typing
- Formula bar editing synchronized with inline editor
- Arrow key navigation between cells
- Tab/Shift+Tab for horizontal navigation
- Enter/Shift+Enter for vertical navigation
- Escape to cancel editing
- Delete/Backspace to clear selected cells
- F2 to enter edit mode
- Copy (Ctrl+C), Cut (Ctrl+X), Paste (Ctrl+V)
- Paste Special dialog: paste values only, formulas only, formatting only
- Undo (Ctrl+Z) / Redo (Ctrl+Y) with full history stack
- Drag-to-autofill handle (numeric increment, formula adjustment, text repeat)

### Formulas
- Formula parser supporting arithmetic (+, -, *, /), comparison (>, <, =, >=, <=, <>), string concatenation (&)
- Cell references: relative (A1), absolute ($A$1), mixed (A$1, $A1)
- Range references (A1:C3)
- Cross-sheet references (Sheet2!A1)
- Functions: SUM, AVERAGE, COUNT, COUNTA, MIN, MAX, ROUND, ABS
- Logic functions: IF, AND, OR, NOT
- Text functions: CONCATENATE, LEN, TRIM, UPPER, LOWER, LEFT, RIGHT, MID
- Date functions: NOW, TODAY
- Dependency graph with automatic recalculation
- Error values: #REF!, #VALUE!, #DIV/0!, #NAME?, #N/A

### Formatting
- Bold (Ctrl+B), Italic (Ctrl+I), Underline (Ctrl+U), Strikethrough
- Font color picker (custom dropdown with 70-color palette)
- Background/fill color picker (same palette)
- Horizontal text alignment: left, center, right
- Vertical text alignment via format
- Number formats: General, Number, Currency ($), Percentage (%), Date, Plain text
- Configurable decimal places
- Cell borders: top, bottom, left, right, all, outer, none; styles: solid, dashed, dotted; configurable color
- Merge & Center, Merge Across, Unmerge
- Conditional formatting rules: greater than, less than, equal to, between, text contains, is empty, is not empty; with background and text color

### Data Features
- Sort ascending/descending on any column
- Multi-column sort dialog with multiple sort keys
- Filter mode toggle (adds dropdown arrows to column headers)
- Filter per column: checkbox filter for unique values; text conditions; number conditions
- Named ranges: define, use in formulas, manage (list/edit/delete) via dialog
- Data validation: dropdown list, number range, text length
- Find and Replace dialog: search text, replace text, match case, match entire cell, search all sheets, find next, replace one, replace all

### Charts
- Chart types: Bar (vertical), Horizontal Bar, Line, Pie, Scatter
- Chart creation from selected data range (Insert > Chart)
- Auto-infer: first row as series labels, first column as categories
- Chart editor panel: chart type selector, data range, chart title, axis labels, legend toggle + position
- Canvas-based rendering with proper axes, gridlines, legends
- Floating overlay: draggable to reposition, resizable via corner handle
- Chart actions: edit, duplicate, delete
- Live updates when underlying data changes

### Multi-Sheet Workbook
- Sheet tabs bar at bottom
- 3 pre-populated sheets on load
- Add new blank sheet via "+" button
- Right-click context menu on tabs: Rename, Duplicate, Delete (with confirmation), Move left, Move right
- Inline renaming on tab
- Active sheet tab is visually highlighted

### Menu Bar Actions
- **File**: New (no-op), Open (no-op), Download as CSV
- **Edit**: Undo, Redo, Cut, Copy, Paste, Paste Special, Find and Replace, Delete row, Delete column, Insert row above, Insert column left
- **View**: Freeze up to current row, Freeze up to current column, Unfreeze, Gridlines toggle, Formula view toggle
- **Insert**: Row above, Row below, Column left, Column right, Chart, Named range
- **Format**: Number format, Bold, Italic, Underline, Text alignment, Cell borders, Merge cells, Conditional formatting
- **Data**: Sort ascending, Sort descending, Multi-column sort, Create filter, Data validation, Named ranges
- **Tools**: Explore (no-op placeholder)

### Toolbar Buttons
Undo, Redo, Bold, Italic, Underline, Strikethrough, Font color, Fill color, Align left, Align center, Align right, Number format, Currency, Percent, Decimal increase/decrease, Borders dropdown, Merge dropdown, Insert chart, Filter toggle

## Data Model

### State Structure (pushed to /api/state)
```
{
  _seedVersion: integer,
  activeSheet: integer (index),
  namedRanges: { name: "SheetName!CellOrRange" },
  sheets: [
    {
      name: string,
      cells: {
        "A1": {
          value: string|number|null,
          formula: string|null (e.g. "=SUM(A1:A10)"),
          format: {
            bold: boolean,
            italic: boolean,
            underline: boolean,
            strikethrough: boolean,
            fontColor: string (hex),
            backgroundColor: string (hex),
            horizontalAlign: "left"|"center"|"right",
            verticalAlign: "top"|"middle"|"bottom",
            numberFormat: "general"|"number"|"currency"|"percentage"|"date"|"text",
            decimalPlaces: integer,
            borderTop: string,
            borderBottom: string,
            borderLeft: string,
            borderRight: string
          },
          validation: { type: string, values: string } (optional)
        }
      },
      columnWidths: { "A": pixels, ... },
      rowHeights: { "1": pixels, ... },
      frozenRows: integer,
      frozenCols: integer,
      mergedCells: ["A1:C1", ...],
      conditionalFormats: [
        {
          range: "A1:A100",
          type: "greater_than"|"less_than"|"equal_to"|"between"|"text_contains"|"is_empty"|"is_not_empty",
          value: string,
          value2: string (for between),
          backgroundColor: string (hex),
          fontColor: string (hex)
        }
      ],
      filters: {
        "A": { type: "values", hiddenValues: [...] }
      },
      filterMode: boolean,
      charts: [
        {
          id: string,
          type: "bar"|"horizontal_bar"|"line"|"pie"|"scatter",
          dataRange: string (e.g. "A1:D10"),
          title: string,
          xAxisLabel: string,
          yAxisLabel: string,
          showLegend: boolean,
          legendPosition: "top"|"bottom"|"left"|"right",
          position: { x: pixels, y: pixels },
          size: { width: pixels, height: pixels },
          colors: [string] (optional)
        }
      ]
    }
  ]
}
```

### Entity Relationships
- Sheets contain cells, charts, conditional formats, filters, merged cell ranges
- Cells may contain formulas that reference other cells (same or cross-sheet)
- Named ranges map names to cell/range references across sheets
- Charts reference data ranges within their parent sheet
- Conditional formats reference cell ranges within their parent sheet

## Navigation Structure
- Single-page app; all content visible at once
- Switch between sheets by clicking sheet tabs at the bottom
- Navigate to any cell by clicking it, using arrow keys, or clicking the cell address label and typing a cell reference
- Access features via Menu Bar (File, Edit, View, Insert, Format, Data) or Toolbar buttons
- Right-click context menus on cells, column headers, row headers, and sheet tabs
- Dialogs opened from menus: Find and Replace, Paste Special, Chart Editor, Conditional Formatting, Named Ranges, Data Validation, Number Format, Sort, Filter, Borders, Merge

## Available Form Controls, Dropdowns, Toggles, and Their Options

### Custom Dropdowns
- **Number Format dropdown** (in Number Format dialog): General, Number, Currency, Percentage, Date, Plain text
- **Conditional Format rule type dropdown**: Greater than, Less than, Equal to, Between, Text contains, Is empty, Is not empty
- **Chart type selector**: Bar, Horizontal Bar, Line, Pie, Scatter
- **Chart legend position dropdown**: Top, Bottom, Left, Right
- **Border style dropdown**: Solid, Dashed, Dotted
- **Data validation type dropdown**: Dropdown list, Number range, Text length
- **Sort order dropdown**: A to Z (ascending), Z to A (descending)

### Toggles
- **Filter mode** (Data menu or toolbar): toggles filter arrows on column headers
- **Gridlines** (View menu): show/hide cell gridlines
- **Formula view** (View menu): show formulas instead of computed values
- **Show legend** (Chart editor): checkbox to show/hide chart legend
- **Match case** (Find and Replace): checkbox
- **Match entire cell** (Find and Replace): checkbox
- **Search all sheets** (Find and Replace): checkbox

### Toolbar Buttons (toggle behavior)
- Bold, Italic, Underline, Strikethrough: toggle on selected cells
- Alignment (left/center/right): sets horizontal alignment

## Seed Data Summary

### Sheet 1: "Sales" (40 data rows + 1 header + 1 summary)
- **Columns**: Date (A), Product (B), Category (C), Region (D), Quantity (E), Unit Price (F), Total (G, formula =E*F), Salesperson (H)
- **Products**: Laptop Pro 15, Wireless Mouse, USB-C Hub, Monitor 27in, Keyboard Mech, Webcam HD, Docking Station, Headset Pro
- **Categories**: Electronics, Accessories, Peripherals
- **Regions**: North, South, East, West
- **Salespeople**: Alex Rivera, Jordan Kim, Casey Chen, Morgan Park, Taylor Singh
- **Dates**: January 2024 through October 2024
- **Summary row 42**: SUM of quantities, AVERAGE of unit prices, SUM of totals
- **Column widths**: customized per column (80-140px)

### Sheet 2: "Employees" (25 data rows + 1 header)
- **Columns**: Name (A), Department (B), Title (C), Salary (D, currency format), Start Date (E), Email (F), Status (G)
- **Departments**: Engineering (8), Sales (4), Marketing (4), HR (3), Finance (4)
- **Titles**: Senior Engineer, Staff Engineer, Junior Developer, Engineering Manager, DevOps Engineer, QA Lead, Frontend Developer, Security Engineer, Sales Director, Sales Rep, Senior Sales Rep, Account Manager, Business Analyst, Marketing Manager, Content Strategist, SEO Specialist, Graphic Designer, Social Media Manager, HR Director, HR Coordinator, Recruiter, CFO, Financial Analyst, Accountant, Payroll Specialist
- **Salary range**: $62,000 - $195,000
- **Start dates**: 2018-2024
- **Status values**: Active (majority), On Leave (2), Contractor (2)
- **Emails**: firstname.lastname@company.com format
- **Names**: Diverse international names (Priya Sharma, Liam O'Brien, Sofia Martinez, Wei Zhang, Amara Okafor, etc.)

### Sheet 3: "Inventory" (30 data rows + 1 header)
- **Columns**: SKU (A), Product Name (B), Category (C), Stock (D), Reorder Level (E), Unit Cost (F, currency format), Supplier (G), Last Restocked (H)
- **SKUs**: SKU-001 through SKU-030
- **Products**: Various tech products (laptops, mice, hubs, monitors, keyboards, webcams, docking stations, headsets, cables, accessories)
- **Categories**: Electronics, Accessories, Peripherals
- **Stock levels**: 0 to 350 (several deliberately below reorder level: SKU-006 stock=8/reorder=40, SKU-007 stock=18/reorder=25, SKU-010 stock=15/reorder=30, SKU-012 stock=12/reorder=20, SKU-014 stock=5/reorder=15, SKU-018 stock=3/reorder=25, SKU-029 stock=0/reorder=30)
- **Suppliers**: TechDist Global, PeriphCo Supply, CableTech Inc, DisplayPro Ltd, KeySwitch Mfg, VisionTech Corp, AudioMax Partners, DeskGear Co, PowerLine Dist
- **Last Restocked dates**: August 2024 through February 2025
