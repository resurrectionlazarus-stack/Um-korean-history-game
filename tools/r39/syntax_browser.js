// [R39] JS 문법 점검(이 PC에는 node가 없다) — built-in 브라우저 콘솔에서 서버의 index.html을 받아 큰 <script>를 V8 new Function 으로 파싱한다.
//  쓰는 법: 아무 페이지(같은 origin · 예 http://127.0.0.1:8046/)에서 콘솔에 붙여 넣고  await __R39SYN("/index.html")
//  결과: { ok, chars, scripts, error }  — error 가 있으면 SyntaxError 메시지(줄 번호는 스크립트 안 기준).
window.__R39SYN = async (path) => {
  const html = await (await fetch(path, { cache: "no-store" })).text();
  const re = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g;
  let m;
  let scripts = 0;
  let big = "";
  while ((m = re.exec(html))) {
    scripts++;
    if (m[1].length > big.length) big = m[1];
  }
  try {
    new Function(big);
    return { ok: true, chars: big.length, scripts, error: null };
  } catch (e) {
    return { ok: false, chars: big.length, scripts, error: String(e && e.message || e) };
  }
};
"R39SYN ready";
