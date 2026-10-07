import {Tiktoken} from 'js-tiktoken/lite';
import cl from 'js-tiktoken/ranks/cl100k_base';
import o from 'js-tiktoken/ranks/o200k_base';
const encs={},ranks={cl100k_base:cl,o200k_base:o};
export function measure(text,name){
 if(!encs[name])encs[name]=new Tiktoken(ranks[name]);
 const enc=encs[name],ids=enc.encode(text,[],[]),decoder=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true});let pos=0;
 const pieces=ids.map(id=>{const bytes=enc.textMap.get(id);let surface=null,valid_utf8=true;
  try{surface=decoder.decode(bytes);}catch{valid_utf8=false;}
  const p={id,hex:[...bytes].map(v=>v.toString(16).padStart(2,'0')).join(' '),byte_start:pos,byte_end:pos+bytes.length,surface,valid_utf8};pos+=bytes.length;return p;
 });
 const raw=new TextEncoder().encode(text),joined=ids.flatMap(id=>[...enc.textMap.get(id)]);
 if(raw.length!==joined.length||joined.some((v,i)=>v!==raw[i]))throw new Error('UTF-8 reconstruction failed');return pieces;
}
