const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const code=fs.readFileSync(__dirname+'/../assets/languages.js','utf8');
function run({path='/',languages=['en-US'],saved=null,ref='',blocked=false,back=false,search='',hash=''}={}){
 let redirect=null,listener,savedValue=saved;
 const context={URL,location:{pathname:path,origin:'https://linuxobservatory.github.io',search,hash,replace:v=>redirect=v},navigator:{languages,language:languages[0]},performance:{getEntriesByType:()=>[{type:back?'back_forward':'navigate'}]},localStorage:{getItem:()=>{if(blocked)throw Error();return savedValue},setItem:(k,v)=>{if(blocked)throw Error();savedValue=v}},document:{referrer:ref,addEventListener:(name,fn)=>listener=fn,querySelectorAll:()=>[]}};
 vm.runInNewContext(code,context);return {redirect,context,listener,getSaved:()=>savedValue};
}
for(const [languages,expected] of [[['da-DK'],'/da/'],[['de-AT'],'/de/'],[['zh-CN'],'/zh-hans/'],[['zh-Hans-SG'],'/zh-hans/'],[['fr-FR','de-DE'],'/de/'],[['en-US','da-DK'],null],[['zh-Hant-TW'],null],[['ja'],null]])assert.equal(run({languages}).redirect,expected);
assert.equal(run({saved:'en',languages:['da']}).redirect,null);
assert.equal(run({saved:'de',languages:['da']}).redirect,'/de/');
assert.equal(run({saved:'invalid',languages:['da']}).redirect,'/da/');
assert.equal(run({blocked:true,languages:['da']}).redirect,'/da/');
assert.equal(run({path:'/about/index.html',languages:['de'],search:'?x=1',hash:'#main'}).redirect,'/de/about/?x=1#main');
for(const lang of ['da','de','zh-hans'])assert.equal(run({path:`/${lang}/about/`,languages:['de'],saved:'en'}).redirect,null);
assert.equal(run({path:'/observations/',languages:['de']}).redirect,null);
assert.equal(run({path:'/about/',languages:['de'],ref:'https://linuxobservatory.github.io/observations/'}).redirect,null);
assert.equal(run({back:true,languages:['de']}).redirect,null);
const r=run({search:'?test=1',hash:'#main'});let click;
const link={href:'https://linuxobservatory.github.io/da/',dataset:{language:'da'},addEventListener:(event,fn)=>click=fn};
r.context.document.querySelectorAll=()=>[link];r.listener();click({button:0});assert.equal(r.getSaved(),'da');assert.equal(link.href,'https://linuxobservatory.github.io/da/?test=1#main');
console.log('PASS: locale variants, preference priority, unavailable storage, deep links, queries/fragments, direct-language URLs, internal links and back navigation.');
