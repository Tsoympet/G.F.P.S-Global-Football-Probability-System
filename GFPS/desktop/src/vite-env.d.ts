/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SECRET_SALT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
