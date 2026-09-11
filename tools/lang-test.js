// Locale-routing tests for public/assets/lang.js — `node tools/lang-test.js`.
// Runs the real script against a stubbed browser and asserts where it sends people.
const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync('public/assets/lang.js','utf8');

function run({path='/',langs=['en-US'],saved=null,query='',referrer='',ua='Mozilla/5.0 Chrome'}){
  let redirected=null, store={}, sess={};
  if(saved) store['sobor.lang']=saved;
  const ctx={
    navigator:{languages:langs,language:langs[0],userAgent:ua},
    location:{pathname:path,search:query,hash:'',host:'sobor.io',
      replace:(u)=>{redirected=u}},
    document:{referrer,addEventListener(){}},
    localStorage:{getItem:k=>store[k]??null,setItem:(k,v)=>{store[k]=v},removeItem:k=>{delete store[k]}},
    sessionStorage:{getItem:k=>sess[k]??null,setItem:(k,v)=>{sess[k]=v},removeItem:k=>{delete sess[k]}},
    history:{replaceState(){}},
    URL, URLSearchParams,
  };
  vm.createContext(ctx);
  vm.runInContext(src,ctx);
  return redirected;
}

const cases=[
 // [description, opts, expected redirect target or null=stay]
 ['English browser on /',            {langs:['en-US','en']},                      null],
 ['Russian browser on /',            {langs:['ru-RU','ru','en']},                 '/ru/'],
 ['Russian browser already on /ru/', {path:'/ru/',langs:['ru-RU']},               null],
 ['Serbian browser -> cnr',          {langs:['sr-RS','en']},                      '/cnr/'],
 ['sr-Latn-ME -> cnr',               {langs:['sr-Latn-ME']},                      '/cnr/'],
 ['Bosnian -> cnr',                  {langs:['bs-BA']},                           '/cnr/'],
 ['Croatian -> cnr',                 {langs:['hr-HR']},                           '/cnr/'],
 ['Montenegrin cnr -> cnr',          {langs:['cnr']},                             '/cnr/'],
 ['cnr browser already on /cnr/',    {path:'/cnr/',langs:['cnr']},                null],
 ['German falls back to en',         {langs:['de-DE']},                           null],
 ['Japanese falls back to en',       {langs:['ja-JP']},                           null],
 ['pref order: en first wins',       {langs:['en-GB','ru']},                      null],
 ['pref order: ru first wins',       {langs:['ru','en-GB']},                      '/ru/'],
 ['saved choice beats browser',      {langs:['ru-RU'],saved:'en'},                null],
 ['saved cnr sends en browser',      {langs:['en-US'],saved:'cnr'},               '/cnr/'],
 ['?lang= beats saved',              {langs:['en'],saved:'ru',query:'?lang=cnr'}, '/cnr/'],
 ['same-site referrer keeps locale', {path:'/ru/',langs:['en-US'],referrer:'https://sobor.io/ru/'}, null],
 ['bots are never redirected',       {langs:['ru-RU'],ua:'Googlebot/2.1'},        null],
 ['GPTBot never redirected',         {langs:['ru-RU'],ua:'GPTBot/1.0'},           null],
 // a shared link to a translated page must survive the recipient's browser
 ['en browser on /cnr/ stays',       {path:'/cnr/',langs:['en-US']},              null],
 ['en browser on /ru/ stays',        {path:'/ru/',langs:['en-US']},               null],
 ['ru browser on /cnr/ stays',       {path:'/cnr/',langs:['ru-RU']},              null],
 ['saved en does not move /cnr/',    {path:'/cnr/',langs:['en'],saved:'en'},      null],
 ['?lang= still overrides the path', {path:'/cnr/',langs:['en'],query:'?lang=ru'},'/ru/'],
 ['?lang= matching path stays',      {path:'/cnr/',langs:['en'],query:'?lang=cnr'},null],
 // the root is still where the browser decides
 ['root + ru browser -> /ru/',       {path:'/',langs:['ru-RU']},                  '/ru/'],
 ['root + sr browser -> /cnr/',      {path:'/',langs:['sr-RS']},                  '/cnr/'],
];
let bad=0;
for(const [d,o,want] of cases){
  const got=run(o);
  const ok=got===want;
  if(!ok)bad++;
  console.log(`${ok?'ok  ':'FAIL'}  ${d.padEnd(34)} -> ${String(got??'(stay)').padEnd(8)} expected ${String(want??'(stay)')}`);
}
console.log(bad ? `\n${bad} of ${cases.length} FAILED` : `\nall ${cases.length} passed`);
process.exit(bad?1:0);
