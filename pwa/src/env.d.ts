declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: string
    VUE_ROUTER_BASE: string | undefined
    VUE_ROUTER_MODE: 'abstract' | 'hash' | 'history' | undefined
    // Define any custom env variables you have here, if you wish
  }
}
