import '@vue/runtime-core'

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $d: (value: Date | number, ...args: any[]) => string
    $n: (value: number, ...args: any[]) => string
    $rt: (message: string, ...args: any[]) => string
    $t: (key: string, ...args: any[]) => string
    $te: (key: string, locale?: string) => boolean
    $tm: (key: string) => any
  }
}

export {}
