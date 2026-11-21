// 用 puppeteer-core + 系统 Chrome 诊断前端页面
// 运行：node .tmp/diag.mjs
import puppeteer from "puppeteer-core";

const browser = await puppeteer.launch({
  executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  headless: true,
  args: ["--no-sandbox", "--disable-gpu"],
});

const page = await browser.newPage();

// 捕获控制台错误
const errors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") errors.push(msg.text());
});
page.on("pageerror", (err) => errors.push("PAGEERROR: " + err.message));

// 捕获网络请求失败
const failedReqs = [];
page.on("requestfailed", (req) => {
  failedReqs.push(req.url() + " -> " + req.failure()?.errorText);
});

console.log("=== 访问 http://127.0.0.1:8000/#/motions ===");
await page.goto("http://127.0.0.1:8000/#/motions", { waitUntil: "networkidle0", timeout: 15000 });

// 等 2 秒让 React 渲染完
await new Promise((r) => setTimeout(r, 2000));

const mainHTML = await page.evaluate(() => {
  const main = document.querySelector("main");
  return main ? main.innerHTML.substring(0, 3000) : "NO MAIN ELEMENT";
});

console.log("\n=== main innerHTML ===");
console.log(mainHTML);

console.log("\n=== 控制台错误 ===");
if (errors.length === 0) console.log("无错误");
else errors.forEach((e) => console.log("  " + e));

console.log("\n=== 失败的网络请求 ===");
if (failedReqs.length === 0) console.log("无失败请求");
else failedReqs.forEach((r) => console.log("  " + r));

// 检查关键内容
const hasText = (text) => mainHTML.includes(text);
console.log("\n=== 内容检查 ===");
console.log("含 '加载中':", hasText("加载中"));
console.log("含 'TEXT-001':", hasText("TEXT-001"));
console.log("含 '关键词揭示':", hasText("关键词揭示"));
console.log("含 video 标签:", mainHTML.includes("<video"));

await browser.close();
