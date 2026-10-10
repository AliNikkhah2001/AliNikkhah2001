declare module 'vis-timeline/dist/vis-timeline-graph2d.esm.js' {
  export interface DataSetOptions {
    fieldId?: string
    type?: { [key: string]: string }
  }

  export class DataSet<T = any> {
    constructor(data?: T[], options?: DataSetOptions)
    add(data: T | T[]): number[]
    update(data: T | T[]): number[]
    remove(id: number | string | number[] | string[]): number[]
    clear(): number[]
    get(id: number | string | number[] | string[]): T | T[]
    getIds(options?: { filter?: (item: T) => boolean; order?: string | ((a: T, b: T) => number) }): number[] | string[]
    forEach(callback: (item: T, id: number | string) => void): void
    map<T2>(callback: (item: T, id: number | string) => T2): T2[]
    length: number
  }

  export interface TimelineOptions {
    stack?: boolean
    height?: string
    minHeight?: string
    editable?: boolean | { add?: boolean; update?: boolean; remove?: boolean }
    showCurrentTime?: boolean
    zoomKey?: string
    max?: Date
    min?: Date
    orientation?: 'top' | 'bottom' | 'both'
    margin?: { item?: number; axis?: number }
    template?: (item: any) => string
    horizontalScroll?: boolean
    verticalScroll?: boolean
    zoomable?: boolean
    selectable?: boolean
    multiselect?: boolean
    zoomMin?: number
    zoomMax?: number
  }

  export interface TimelineItem {
    id: string | number
    content: string
    start: string | Date
    end?: string | Date
    type?: 'box' | 'point' | 'range' | 'background'
    className?: string
    title?: string
    group?: string | number
    subgroup?: string | number
  }

  export class Timeline {
    constructor(container: HTMLElement, items: DataSet | TimelineItem[], options?: TimelineOptions)
    destroy(): void
    setItems(items: DataSet | TimelineItem[]): void
    setGroups(groups: any[]): void
    setOptions(options: TimelineOptions): void
    fit(options?: { animation?: boolean }): void
    moveTo(time: Date | string | number, options?: { animation?: boolean }): void
    zoomIn(percentage: number, options?: { animation?: boolean }): void
    zoomOut(percentage: number, options?: { animation?: boolean }): void
    on(event: string, callback: (...args: any[]) => void): void
    off(event: string, callback: (...args: any[]) => void): void
    getWindow(): { start: Date; end: Date }
    getVisibleItems(): number[]
    getSelection(): number[]
    setSelection(selection: number | number[], options?: { focus?: boolean; animation?: boolean }): void
    getItemRange(): { min: Date; max: Date }
    getEventProperties(event: MouseEvent): any
  }

  const Timeline: { new (container: HTMLElement, items: DataSet | TimelineItem[], options?: TimelineOptions): Timeline }
  export { DataSet }
  export default Timeline
}