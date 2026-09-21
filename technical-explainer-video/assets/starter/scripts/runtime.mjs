import {createServer} from 'vite';
import {chromium} from 'playwright';
import {fileURLToPath} from 'node:url';
export const root=fileURLToPath(new URL('../',import.meta.url));
export async function runtime(){
 const server=await createServer({root,configFile:root+'vite.config.ts',server:{host:'127.0.0.1',port:0,strictPort:true}});
 try{
  await server.listen();
  const address=server.httpServer.address();
  const channel=process.env.BROWSER_CHANNEL??'chrome';
  const browser=await chromium.launch({...(channel==='chromium'?{}:{channel}),headless:true,args:['--disable-background-timer-throttling','--autoplay-policy=no-user-gesture-required']});
  return{browser,url:`http://127.0.0.1:${address.port}`,close:async()=>{try{await browser.close();}finally{await server.close();}}};
 }catch(error){await server.close();throw error;}
}
