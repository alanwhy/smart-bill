/**
 * Excel 工具函数 — 账单导入/导出
 *
 * 列定义：金额 | 商家名称 | 交易日期 | 分类名称 | 备注
 */
import * as XLSX from 'xlsx'
import type { BillRecord, Category } from '@/types/bill'

// ---------------------------------------------------------------------------
// 常量
// ---------------------------------------------------------------------------

export const EXCEL_COLUMNS = ['金额', '商家名称', '交易日期', '分类名称', '备注'] as const

const TEMPLATE_EXAMPLE = [
  {
    金额: -50.0,
    商家名称: '麦当劳',
    交易日期: '2026-06-18',
    分类名称: '餐饮',
    备注: '午饭',
  },
  {
    金额: 8000.0,
    商家名称: '公司工资',
    交易日期: '2026-06-01',
    分类名称: '工资收入',
    备注: '',
  },
]

const FIELD_INSTRUCTIONS = [
  ['字段说明'],
  ['金额', '数字，负数=支出，正数=收入，不能为 0'],
  ['商家名称', '文字，不能为空'],
  ['交易日期', '格式 YYYY-MM-DD，如 2026-06-18'],
  ['分类名称', '须与系统中已有分类名称完全匹配'],
  ['备注', '可选，最多 100 字'],
]

// ---------------------------------------------------------------------------
// 下载模板
// ---------------------------------------------------------------------------

export function downloadTemplate(categoryNames: string[] = []): void {
  const wb = XLSX.utils.book_new()

  // Sheet1: 数据填写区
  const dataSheet = XLSX.utils.json_to_sheet(TEMPLATE_EXAMPLE, { header: [...EXCEL_COLUMNS] })

  // 设置列宽
  dataSheet['!cols'] = [
    { wch: 12 }, // 金额
    { wch: 20 }, // 商家名称
    { wch: 14 }, // 交易日期
    { wch: 16 }, // 分类名称
    { wch: 20 }, // 备注
  ]

  XLSX.utils.book_append_sheet(wb, dataSheet, '账单数据')

  // Sheet2: 说明 + 可用分类列表
  const infoRows: string[][] = [
    ...FIELD_INSTRUCTIONS,
    [],
    ['可用分类名称（复制到「分类名称」列）'],
    ...categoryNames.map((n) => [n]),
  ]
  const infoSheet = XLSX.utils.aoa_to_sheet(infoRows)
  infoSheet['!cols'] = [{ wch: 20 }, { wch: 40 }]
  XLSX.utils.book_append_sheet(wb, infoSheet, '填写说明')

  XLSX.writeFile(wb, '账单导入模板.xlsx')
}

// ---------------------------------------------------------------------------
// 导出账单
// ---------------------------------------------------------------------------

export function exportBillsToExcel(bills: BillRecord[], filename: string): void {
  const rows = bills.map((b) => ({
    金额: b.value,
    商家名称: b.merchant_name,
    交易日期: b.transaction_date.slice(0, 10),
    分类名称: b.category?.name ?? '',
    备注: b.description ?? '',
  }))

  const ws = XLSX.utils.json_to_sheet(rows, { header: [...EXCEL_COLUMNS] })
  ws['!cols'] = [{ wch: 12 }, { wch: 20 }, { wch: 14 }, { wch: 16 }, { wch: 24 }]

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '账单')
  XLSX.writeFile(wb, filename)
}

// ---------------------------------------------------------------------------
// 解析导入文件
// ---------------------------------------------------------------------------

export interface ImportBillRow {
  value: number
  merchant_name: string
  transaction_date: string
  category_name: string
  description: string
  category_id?: number
}

export interface ParseResult {
  rows: ImportBillRow[]
  errors: Array<{ row: number; field: string; message: string }>
}

/** 将 Excel 序列号日期转为 YYYY-MM-DD 字符串 */
function excelDateToString(value: unknown): string | null {
  if (value === null || value === undefined || value === '') return null
  // 已是字符串，尝试直接识别
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (/^\d{4}-\d{2}-\d{2}/.test(trimmed)) return trimmed.slice(0, 10)
    // 尝试解析其他格式
    const d = new Date(trimmed)
    if (!isNaN(d.getTime())) return d.toISOString().slice(0, 10)
    return null
  }
  // 数字：Excel 序列日期
  if (typeof value === 'number') {
    const d = XLSX.SSF.parse_date_code(value)
    if (!d) return null
    const month = String(d.m).padStart(2, '0')
    const day = String(d.d).padStart(2, '0')
    return `${d.y}-${month}-${day}`
  }
  return null
}

export function parseImportFile(
  file: File,
  categories: Category[],
): Promise<ParseResult> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      try {
        const data = e.target?.result
        const wb = XLSX.read(data, { type: 'array', cellDates: false })

        const sheetName = wb.SheetNames[0]
        if (!sheetName) {
          return resolve({ rows: [], errors: [{ row: 0, field: '文件', message: 'Excel 文件中没有任何 Sheet' }] })
        }

        const ws = wb.Sheets[sheetName]
        const rawRows: Record<string, unknown>[] = XLSX.utils.sheet_to_json(ws, {
          defval: '',
          raw: true,
        })

        if (rawRows.length === 0) {
          return resolve({ rows: [], errors: [{ row: 0, field: '文件', message: '表格中没有数据行（第一行为表头）' }] })
        }

        // 构建分类名称 → category_id 映射（大小写不敏感）
        const categoryMap = new Map<string, number>()
        categories.forEach((c) => categoryMap.set(c.name.toLowerCase(), c.id))

        const rows: ImportBillRow[] = []
        const errors: ParseResult['errors'] = []

        rawRows.forEach((raw, idx) => {
          const rowNum = idx + 2 // Excel 行号（1 为表头，数据从 2 开始）

          // 金额
          const rawValue = raw['金额']
          const value = typeof rawValue === 'number' ? rawValue : parseFloat(String(rawValue))
          if (rawValue === '' || rawValue === undefined || rawValue === null) {
            errors.push({ row: rowNum, field: '金额', message: '必填项不能为空' })
          } else if (isNaN(value)) {
            errors.push({ row: rowNum, field: '金额', message: `「${rawValue}」不是有效数字` })
          } else if (value === 0) {
            errors.push({ row: rowNum, field: '金额', message: '金额不能为 0' })
          }

          // 商家名称
          const merchantName = String(raw['商家名称'] ?? '').trim()
          if (!merchantName) {
            errors.push({ row: rowNum, field: '商家名称', message: '必填项不能为空' })
          }

          // 交易日期
          const dateStr = excelDateToString(raw['交易日期'])
          if (!dateStr) {
            errors.push({ row: rowNum, field: '交易日期', message: `「${raw['交易日期']}」格式不正确，须为 YYYY-MM-DD` })
          } else {
            const d = new Date(dateStr)
            if (isNaN(d.getTime())) {
              errors.push({ row: rowNum, field: '交易日期', message: `「${dateStr}」不是合法日期` })
            }
          }

          // 分类名称
          const categoryName = String(raw['分类名称'] ?? '').trim()
          if (!categoryName) {
            errors.push({ row: rowNum, field: '分类名称', message: '必填项不能为空' })
          } else {
            const categoryId = categoryMap.get(categoryName.toLowerCase())
            if (!categoryId) {
              errors.push({
                row: rowNum,
                field: '分类名称',
                message: `「${categoryName}」与系统中的分类名称不匹配，请检查填写说明`,
              })
            }
          }

          // 备注（可选，超长截断并记录警告，不作为错误）
          let description = String(raw['备注'] ?? '').trim()
          if (description.length > 100) {
            description = description.slice(0, 100)
          }

          rows.push({
            value: isNaN(value) ? 0 : value,
            merchant_name: merchantName,
            transaction_date: dateStr ?? '',
            category_name: categoryName,
            description,
            category_id: categoryMap.get(categoryName.toLowerCase()),
          })
        })

        resolve({ rows, errors })
      } catch (err) {
        reject(new Error(`解析 Excel 文件失败：${String(err)}`))
      }
    }

    reader.onerror = () => reject(new Error('读取文件失败'))
    reader.readAsArrayBuffer(file)
  })
}
