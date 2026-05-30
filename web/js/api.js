const API_BASE = "http://127.0.0.1:5000";
async function apiGet(path){try{const r=await fetch(API_BASE+path);return await r.json()}catch(e){console.error(e);return{code:500,message:e.message}}}
async function apiPost(path,data){try{const r=await fetch(API_BASE+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});return await r.json()}catch(e){return{code:500,message:e.message}}}
async function apiDelete(path){try{const r=await fetch(API_BASE+path,{method:"DELETE"});return await r.json()}catch(e){return{code:500,message:e.message}}}