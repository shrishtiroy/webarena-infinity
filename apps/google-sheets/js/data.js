const SEED_DATA_VERSION = 1;

function getSeedData() {
    return {
        _seedVersion: SEED_DATA_VERSION,
        activeSheet: 0,
        namedRanges: {},
        sheets: [
            createSalesSheet(),
            createEmployeesSheet(),
            createInventorySheet()
        ]
    };
}

function createEmptySheetState(name) {
    return {
        name: name,
        cells: {},
        columnWidths: {},
        rowHeights: {},
        frozenRows: 0,
        frozenCols: 0,
        mergedCells: [],
        conditionalFormats: [],
        filters: {},
        filterMode: false,
        charts: []
    };
}

function cell(value, formula, format) {
    return {
        value: value,
        formula: formula || null,
        format: format || {}
    };
}

function headerCell(value) {
    return cell(value, null, { bold: true, backgroundColor: '#e8eaed', horizontalAlign: 'center' });
}

function createSalesSheet() {
    const sheet = createEmptySheetState('Sales');

    const headers = ['Date', 'Product', 'Category', 'Region', 'Quantity', 'Unit Price', 'Total', 'Salesperson'];
    const cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
    cols.forEach((c, i) => {
        sheet.cells[c + '1'] = headerCell(headers[i]);
    });

    const products = [
        { name: 'Laptop Pro 15', cat: 'Electronics', prices: [849.00, 899.00, 879.50] },
        { name: 'Wireless Mouse', cat: 'Accessories', prices: [29.99, 34.99, 24.99] },
        { name: 'USB-C Hub', cat: 'Accessories', prices: [49.99, 59.99, 45.00] },
        { name: 'Monitor 27in', cat: 'Peripherals', prices: [349.00, 399.00, 329.00] },
        { name: 'Keyboard Mech', cat: 'Peripherals', prices: [79.99, 89.99, 74.50] },
        { name: 'Webcam HD', cat: 'Peripherals', prices: [69.99, 64.99, 74.99] },
        { name: 'Docking Station', cat: 'Electronics', prices: [199.50, 219.00, 189.00] },
        { name: 'Headset Pro', cat: 'Accessories', prices: [129.99, 149.99, 119.00] }
    ];
    const regions = ['North', 'South', 'East', 'West'];
    const salespeople = ['Alex Rivera', 'Jordan Kim', 'Casey Chen', 'Morgan Park', 'Taylor Singh'];

    const salesData = [
        ['01/05/2024', 0, 'North', 12, 0, 'Alex Rivera'],
        ['01/12/2024', 1, 'South', 45, 0, 'Jordan Kim'],
        ['01/18/2024', 3, 'East', 3, 1, 'Casey Chen'],
        ['01/25/2024', 4, 'West', 28, 0, 'Morgan Park'],
        ['02/02/2024', 5, 'North', 8, 1, 'Taylor Singh'],
        ['02/09/2024', 2, 'South', 35, 1, 'Alex Rivera'],
        ['02/15/2024', 6, 'East', 5, 0, 'Jordan Kim'],
        ['02/22/2024', 7, 'North', 15, 2, 'Casey Chen'],
        ['03/01/2024', 0, 'West', 7, 1, 'Morgan Park'],
        ['03/08/2024', 1, 'South', 50, 1, 'Taylor Singh'],
        ['03/14/2024', 3, 'North', 2, 0, 'Alex Rivera'],
        ['03/20/2024', 4, 'East', 42, 2, 'Jordan Kim'],
        ['03/28/2024', 5, 'South', 11, 0, 'Casey Chen'],
        ['04/03/2024', 2, 'West', 22, 0, 'Morgan Park'],
        ['04/10/2024', 6, 'North', 4, 1, 'Taylor Singh'],
        ['04/18/2024', 7, 'East', 19, 0, 'Alex Rivera'],
        ['04/25/2024', 0, 'South', 9, 2, 'Jordan Kim'],
        ['05/02/2024', 1, 'North', 38, 2, 'Casey Chen'],
        ['05/10/2024', 3, 'West', 6, 0, 'Morgan Park'],
        ['05/17/2024', 4, 'South', 31, 1, 'Taylor Singh'],
        ['05/24/2024', 5, 'East', 14, 2, 'Alex Rivera'],
        ['06/01/2024', 2, 'North', 27, 1, 'Jordan Kim'],
        ['06/08/2024', 6, 'South', 3, 0, 'Casey Chen'],
        ['06/15/2024', 7, 'West', 21, 1, 'Morgan Park'],
        ['06/22/2024', 0, 'East', 10, 0, 'Taylor Singh'],
        ['07/01/2024', 1, 'North', 44, 0, 'Alex Rivera'],
        ['07/08/2024', 3, 'South', 1, 2, 'Jordan Kim'],
        ['07/15/2024', 4, 'West', 36, 2, 'Casey Chen'],
        ['07/22/2024', 5, 'East', 7, 1, 'Morgan Park'],
        ['08/01/2024', 2, 'North', 18, 0, 'Taylor Singh'],
        ['08/10/2024', 6, 'South', 9, 2, 'Alex Rivera'],
        ['08/18/2024', 7, 'North', 25, 0, 'Jordan Kim'],
        ['08/25/2024', 0, 'West', 5, 1, 'Casey Chen'],
        ['09/03/2024', 1, 'East', 33, 1, 'Morgan Park'],
        ['09/12/2024', 3, 'South', 4, 0, 'Taylor Singh'],
        ['09/20/2024', 4, 'North', 20, 0, 'Alex Rivera'],
        ['09/28/2024', 5, 'West', 16, 2, 'Jordan Kim'],
        ['10/05/2024', 2, 'East', 40, 2, 'Casey Chen'],
        ['10/15/2024', 6, 'North', 2, 1, 'Morgan Park'],
        ['10/25/2024', 7, 'South', 30, 0, 'Taylor Singh']
    ];

    salesData.forEach((row, i) => {
        const r = i + 2;
        const prod = products[row[1]];
        const price = prod.prices[row[4]];
        const qty = row[3];
        sheet.cells['A' + r] = cell(row[0]);
        sheet.cells['B' + r] = cell(prod.name);
        sheet.cells['C' + r] = cell(prod.cat);
        sheet.cells['D' + r] = cell(row[2]);
        sheet.cells['E' + r] = cell(qty);
        sheet.cells['F' + r] = cell(price, null, { numberFormat: 'currency' });
        sheet.cells['G' + r] = cell(qty * price, '=E' + r + '*F' + r, { numberFormat: 'currency' });
        sheet.cells['H' + r] = cell(row[5]);
    });

    // Summary row 42
    sheet.cells['D42'] = cell('Totals:', null, { bold: true });
    sheet.cells['E42'] = cell(null, '=SUM(E2:E41)', { bold: true });
    sheet.cells['F42'] = cell(null, '=AVERAGE(F2:F41)', { bold: true, numberFormat: 'currency' });
    sheet.cells['G42'] = cell(null, '=SUM(G2:G41)', { bold: true, numberFormat: 'currency' });

    sheet.columnWidths = { A: 100, B: 140, C: 110, D: 80, E: 80, F: 100, G: 110, H: 120 };

    return sheet;
}

function createEmployeesSheet() {
    const sheet = createEmptySheetState('Employees');

    const headers = ['Name', 'Department', 'Title', 'Salary', 'Start Date', 'Email', 'Status'];
    const cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
    cols.forEach((c, i) => {
        sheet.cells[c + '1'] = headerCell(headers[i]);
    });

    const employees = [
        ['Priya Sharma', 'Engineering', 'Senior Engineer', 125000, '03/15/2019', 'priya.sharma@company.com', 'Active'],
        ['Liam O\'Brien', 'Engineering', 'Staff Engineer', 155000, '06/01/2018', 'liam.obrien@company.com', 'Active'],
        ['Sofia Martinez', 'Engineering', 'Junior Developer', 78000, '09/10/2023', 'sofia.martinez@company.com', 'Active'],
        ['Wei Zhang', 'Engineering', 'Engineering Manager', 165000, '01/20/2020', 'wei.zhang@company.com', 'Active'],
        ['Amara Okafor', 'Engineering', 'DevOps Engineer', 118000, '04/05/2021', 'amara.okafor@company.com', 'On Leave'],
        ['James Wilson', 'Sales', 'Sales Director', 140000, '11/12/2018', 'james.wilson@company.com', 'Active'],
        ['Elena Popov', 'Sales', 'Sales Rep', 72000, '08/22/2022', 'elena.popov@company.com', 'Active'],
        ['Marcus Brown', 'Sales', 'Senior Sales Rep', 95000, '03/01/2020', 'marcus.brown@company.com', 'Active'],
        ['Yuki Tanaka', 'Sales', 'Account Manager', 105000, '07/15/2021', 'yuki.tanaka@company.com', 'Contractor'],
        ['Fatima Al-Hassan', 'Marketing', 'Marketing Manager', 115000, '02/28/2019', 'fatima.alhassan@company.com', 'Active'],
        ['Noah Davis', 'Marketing', 'Content Strategist', 82000, '05/10/2022', 'noah.davis@company.com', 'Active'],
        ['Isabella Rossi', 'Marketing', 'SEO Specialist', 76000, '10/01/2023', 'isabella.rossi@company.com', 'Active'],
        ['Raj Patel', 'Marketing', 'Graphic Designer', 71000, '12/05/2021', 'raj.patel@company.com', 'On Leave'],
        ['Chloe Dupont', 'HR', 'HR Director', 135000, '08/15/2018', 'chloe.dupont@company.com', 'Active'],
        ['David Kim', 'HR', 'HR Coordinator', 62000, '01/10/2024', 'david.kim@company.com', 'Active'],
        ['Aisha Mohammed', 'HR', 'Recruiter', 68000, '06/20/2022', 'aisha.mohammed@company.com', 'Active'],
        ['Oliver Grant', 'Finance', 'CFO', 195000, '04/01/2018', 'oliver.grant@company.com', 'Active'],
        ['Hannah Lee', 'Finance', 'Financial Analyst', 88000, '09/15/2021', 'hannah.lee@company.com', 'Active'],
        ['Samuel Nguyen', 'Finance', 'Accountant', 75000, '11/20/2020', 'samuel.nguyen@company.com', 'Active'],
        ['Zara Thompson', 'Finance', 'Payroll Specialist', 65000, '03/08/2023', 'zara.thompson@company.com', 'Contractor'],
        ['Erik Johansson', 'Engineering', 'QA Lead', 110000, '05/22/2019', 'erik.johansson@company.com', 'Active'],
        ['Maya Rodriguez', 'Engineering', 'Frontend Developer', 98000, '08/14/2022', 'maya.rodriguez@company.com', 'Active'],
        ['Chen Wei-Lin', 'Sales', 'Business Analyst', 90000, '02/10/2021', 'chen.weilin@company.com', 'Active'],
        ['Olivia Andersson', 'Engineering', 'Security Engineer', 132000, '10/30/2020', 'olivia.andersson@company.com', 'Active'],
        ['Lucas Silva', 'Marketing', 'Social Media Manager', 69000, '07/01/2023', 'lucas.silva@company.com', 'Active']
    ];

    employees.forEach((emp, i) => {
        const r = i + 2;
        sheet.cells['A' + r] = cell(emp[0]);
        sheet.cells['B' + r] = cell(emp[1]);
        sheet.cells['C' + r] = cell(emp[2]);
        sheet.cells['D' + r] = cell(emp[3], null, { numberFormat: 'currency' });
        sheet.cells['E' + r] = cell(emp[4]);
        sheet.cells['F' + r] = cell(emp[5]);
        sheet.cells['G' + r] = cell(emp[6]);
    });

    sheet.columnWidths = { A: 160, B: 110, C: 150, D: 100, E: 100, F: 230, G: 90 };

    return sheet;
}

function createInventorySheet() {
    const sheet = createEmptySheetState('Inventory');

    const headers = ['SKU', 'Product Name', 'Category', 'Stock', 'Reorder Level', 'Unit Cost', 'Supplier', 'Last Restocked'];
    const cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
    cols.forEach((c, i) => {
        sheet.cells[c + '1'] = headerCell(headers[i]);
    });

    const inventory = [
        ['SKU-001', 'Laptop Pro 15', 'Electronics', 45, 20, 620.00, 'TechDist Global', '01/10/2025'],
        ['SKU-002', 'Laptop Pro 13', 'Electronics', 32, 15, 540.00, 'TechDist Global', '12/20/2024'],
        ['SKU-003', 'Wireless Mouse', 'Accessories', 230, 100, 12.50, 'PeriphCo Supply', '02/01/2025'],
        ['SKU-004', 'Wireless Mouse Ergo', 'Accessories', 85, 50, 18.75, 'PeriphCo Supply', '01/15/2025'],
        ['SKU-005', 'USB-C Hub 7-port', 'Accessories', 120, 60, 22.00, 'CableTech Inc', '01/25/2025'],
        ['SKU-006', 'USB-C Hub 4-port', 'Accessories', 8, 40, 15.00, 'CableTech Inc', '11/05/2024'],
        ['SKU-007', 'Monitor 27in 4K', 'Peripherals', 18, 25, 215.00, 'DisplayPro Ltd', '12/12/2024'],
        ['SKU-008', 'Monitor 24in FHD', 'Peripherals', 55, 30, 145.00, 'DisplayPro Ltd', '01/30/2025'],
        ['SKU-009', 'Keyboard Mech RGB', 'Peripherals', 72, 40, 38.00, 'KeySwitch Mfg', '02/05/2025'],
        ['SKU-010', 'Keyboard Mech TKL', 'Peripherals', 15, 30, 42.00, 'KeySwitch Mfg', '10/22/2024'],
        ['SKU-011', 'Webcam HD 1080p', 'Peripherals', 90, 50, 28.00, 'VisionTech Corp', '01/18/2025'],
        ['SKU-012', 'Webcam 4K Pro', 'Peripherals', 12, 20, 55.00, 'VisionTech Corp', '11/30/2024'],
        ['SKU-013', 'Docking Station USB-C', 'Electronics', 38, 25, 95.00, 'TechDist Global', '01/05/2025'],
        ['SKU-014', 'Docking Station TB4', 'Electronics', 5, 15, 140.00, 'TechDist Global', '09/15/2024'],
        ['SKU-015', 'Headset Pro Wireless', 'Accessories', 67, 35, 62.00, 'AudioMax Partners', '02/08/2025'],
        ['SKU-016', 'Headset Pro Wired', 'Accessories', 110, 50, 45.00, 'AudioMax Partners', '01/20/2025'],
        ['SKU-017', 'Laptop Stand Aluminum', 'Accessories', 42, 30, 28.00, 'DeskGear Co', '12/01/2024'],
        ['SKU-018', 'Desk Mat XL', 'Accessories', 3, 25, 14.00, 'DeskGear Co', '10/10/2024'],
        ['SKU-019', 'Power Strip Smart', 'Electronics', 95, 40, 32.00, 'PowerLine Dist', '01/28/2025'],
        ['SKU-020', 'UPS Battery 600VA', 'Electronics', 22, 15, 78.00, 'PowerLine Dist', '11/20/2024'],
        ['SKU-021', 'Ethernet Cable 10ft', 'Accessories', 350, 200, 3.50, 'CableTech Inc', '02/10/2025'],
        ['SKU-022', 'HDMI Cable 6ft', 'Accessories', 280, 150, 5.25, 'CableTech Inc', '02/10/2025'],
        ['SKU-023', 'Surge Protector 8-out', 'Electronics', 60, 30, 18.00, 'PowerLine Dist', '01/12/2025'],
        ['SKU-024', 'Laptop Bag 15in', 'Accessories', 48, 25, 22.00, 'DeskGear Co', '12/15/2024'],
        ['SKU-025', 'Mousepad Gaming XL', 'Accessories', 135, 75, 8.50, 'PeriphCo Supply', '01/22/2025'],
        ['SKU-026', 'USB Flash Drive 64GB', 'Accessories', 200, 100, 6.00, 'TechDist Global', '02/01/2025'],
        ['SKU-027', 'External SSD 1TB', 'Electronics', 28, 20, 65.00, 'TechDist Global', '12/28/2024'],
        ['SKU-028', 'Monitor Arm Single', 'Peripherals', 35, 20, 42.00, 'DeskGear Co', '01/08/2025'],
        ['SKU-029', 'Wireless Charger Pad', 'Accessories', 0, 30, 12.00, 'PowerLine Dist', '08/20/2024'],
        ['SKU-030', 'Noise Cancelling Earbuds', 'Accessories', 52, 25, 48.00, 'AudioMax Partners', '01/15/2025']
    ];

    inventory.forEach((item, i) => {
        const r = i + 2;
        sheet.cells['A' + r] = cell(item[0]);
        sheet.cells['B' + r] = cell(item[1]);
        sheet.cells['C' + r] = cell(item[2]);
        sheet.cells['D' + r] = cell(item[3]);
        sheet.cells['E' + r] = cell(item[4]);
        sheet.cells['F' + r] = cell(item[5], null, { numberFormat: 'currency' });
        sheet.cells['G' + r] = cell(item[6]);
        sheet.cells['H' + r] = cell(item[7]);
    });

    sheet.columnWidths = { A: 80, B: 180, C: 110, D: 70, E: 110, F: 90, G: 150, H: 120 };

    return sheet;
}
