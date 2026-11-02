import{cp,mkdir}from'node:fs/promises';import{fileURLToPath}from'node:url';import{dirname,resolve}from'node:path';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../..');
await mkdir(resolve(here,'../public/assets'),{recursive:true});await cp(resolve(root,'assets'),resolve(here,'../public/assets'),{recursive:true});
console.log('Prepared the existing public assets for local development.');
