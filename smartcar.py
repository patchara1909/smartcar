import http.server
import socketserver
from urllib.parse import urlparse

HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SmartCar — EV Shuttle University</title>
  <style>
    :root {
      --bg: #07111f;
      --panel: #111d31;
      --panel-2: #16253d;
      --accent: #4fd1c5;
      --accent-2: #7c9cff;
      --text: #f5f7fb;
      --muted: #9fb0c8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      color: var(--text);
      background: linear-gradient(135deg, var(--bg), #0f1f37 60%, #142a4a);
      min-height: 100vh;
    }
    .app {
      max-width: 1100px;
      margin: 0 auto;
      padding: 24px;
    }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background: rgba(17, 29, 49, 0.85);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 18px;
      backdrop-filter: blur(10px);
    }
    .brand { font-size: 1.3rem; font-weight: 700; }
    .pill { background: rgba(79,209,197,0.16); color: var(--accent); padding: 8px 12px; border-radius: 999px; font-size: 0.9rem; }
    .hero {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 20px;
      margin-top: 20px;
    }
    .card {
      background: rgba(17,29,49,0.9);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 22px;
      padding: 20px;
      box-shadow: 0 18px 45px rgba(0,0,0,0.22);
    }
    h1 { font-size: 2rem; margin: 0 0 8px; }
    p { color: var(--muted); line-height: 1.6; }
    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px; }
    .stat { background: var(--panel-2); padding: 12px; border-radius: 14px; }
    .stat strong { display: block; font-size: 1.05rem; }
    form { display: grid; gap: 12px; margin-top: 14px; }
    label { font-size: 0.95rem; color: var(--muted); }
    select, input, button {
      width: 100%; padding: 12px 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.11); font-size: 1rem;
    }
    input, select { background: #0d1729; color: var(--text); }
    button {
      cursor: pointer; background: linear-gradient(90deg, var(--accent), var(--accent-2)); color: #03111f; font-weight: 700; border: none;
    }
    .status { margin-top: 16px; padding: 14px; border-radius: 14px; background: rgba(79,209,197,0.13); border: 1px solid rgba(79,209,197,0.35); }
    .mini-map {
      height: 220px; border-radius: 18px; margin-top: 16px; background: linear-gradient(120deg, rgba(79,209,197,0.18), rgba(124,156,255,0.16)); position: relative; overflow: hidden;
    }
    .dot { position: absolute; width: 14px; height: 14px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 8px rgba(79,209,197,0.18); }
    .dot.a { top: 28%; left: 24%; }
    .dot.b { top: 58%; left: 70%; }
    .route { position: absolute; inset: 0; background: repeating-linear-gradient(120deg, transparent, transparent 40px, rgba(255,255,255,0.06) 40px, rgba(255,255,255,0.06) 46px); }
    @media (max-width: 820px) {
      .hero { grid-template-columns: 1fr; }
      .stats { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="app">
    <div class="topbar">
      <div class="brand">⚡ SmartCar</div>
      <div class="pill">EV Shuttle • University Demo</div>
    </div>

    <div class="hero">
      <div class="card">
        <h1>เรียกรถไฟฟ้าภายในมหาวิทยาลัย</h1>
        <p>ตัวอย่างเว็บจำลองแอปสำหรับแสดงผลงาน โดยเน้นการสั่งรถอัจฉริยะจากจุดรับ-ปลายทางภายใน campus แบบเรียบง่ายและทันสมัย</p>
        <div class="stats">
          <div class="stat"><strong>2–4 นาที</strong><span>เวลาถึง</span></div>
          <div class="stat"><strong>100% EV</strong><span>พลังงานสะอาด</span></div>
          <div class="stat"><strong>24/7</strong><span>ให้บริการ</span></div>
        </div>
        <form id="rideForm">
          <label>จุดขึ้นรถ</label>
          <select id="pickup">
           <option>หอพักนักศึกษาทะเลแก้วนิเวศ 1</option>
           <option>หอพักนักศึกษาทะเลแก้วนิเวศ 2</option>
           <option>หอพักนักศึกษาทะเลแก้วนิเวศ 3</option>
           <option>หอพักนักศึกษาชายกาซะลอง</option>
            <option>คณะเทคโนโลยีอุตสาหกรรม</option>
             <option>คณะเทคโนโลยีการเกษตรและอาหาร</option>
            <option>คณะพยาบาลศาสตร์</option>
            <option>คณะมนุษยศาสตร์</option>
            <option>คณะสังคมศาสตร์และการพัฒนาท้องถิ่น</option>
            <option>คณะวิทยาศาสตร์</option>
            <option>คณะวิทยาการการจัดการ</option>
            <option>โรงอาหารหอพักทะเลแก้วนิเวศ</option>
            <option>อาคารพิบูลวิทย์</option>
            <option>อาคารทีประวิญช์</option>
            <option>หอประชุมศรีสชิระโชติ</option>
            <option>ตึก IT</option>
            <option>ห้องสมุด</option>
            <option>สนามกีฬาพระองค์ดำ</option>
          </select>

          <label>ปลายทาง</label>
          <select id="dropoff">
           <option>หอพักนักศึกษาทะเลแก้วนิเวศ 1</option>
           <option>หอพักนักศึกษาทะเลแก้วนิเวศ 2</option>
           <option>หอพักนักศึกษาทะเลแก้วนิเวศ 3</option>
           <option>หอพักนักศึกษาชายกาซะลอง</option>
            <option>คณะเทคโนโลยีอุตสาหกรรม</option>
            <option>คณะเทคโนโลยีการเกษตรและอาหาร</option>
            <option>คณะพยาบาลศาสตร์</option>
            <option>คณะมนุษยศาสตร์</option>
            <option>คณะสังคมศาสตร์และการพัฒนาท้องถิ่น</option>
            <option>คณะวิทยาศาสตร์</option>
            <option>คณะวิทยาการการจัดการ</option>
            <option>โรงอาหารหอพักทะเลแก้วนิเวศ</option>
            <option>อาคารพิบูลวิทย์</option>
            <option>อาคารทีประวิญช์</option>
            <option>หอประชุมศรีสชิระโชติ</option>
            <option>ตึก IT</option>
            <option>ห้องสมุด</option>
            <option>สนามกีฬาพระองค์ดำ</option>
          </select>

          <label>จำนวนผู้โดยสาร</label>
          <input id="people" type="number" min="1" max="6" value="2" />

          <button type="submit">เรียกรถตอนนี้</button>
        </form>
        <div id="status" class="status">สถานะ: กำลังค้นหารถที่ใกล้ที่สุด...</div>
      </div>

      <div class="card">
        <h3>แผนที่จำลองการเดินทาง</h3>
        <div class="mini-map">
          <div class="route"></div>
          <div class="dot a"></div>
          <div class="dot b"></div>
        </div>
        <p id="summary">รถ EV กำลังเตรียมพร้อมสำหรับเส้นทางจากหอพักนักศึกษาทะเลแก้วนิเวศ 1 ไปยังห้องสมุด</p>
      </div>
    </div>
  </div>

  <script>
    const form = document.getElementById('rideForm');
    const status = document.getElementById('status');
    const summary = document.getElementById('summary');

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const pickup = document.getElementById('pickup').value;
      const dropoff = document.getElementById('dropoff').value;
      const people = document.getElementById('people').value;
      const minutes = Math.max(2, Math.min(6, 2 + Math.abs(people) + (pickup.length + dropoff.length) % 3));

      status.innerHTML = `สถานะ: รถ EV ได้รับคำขอแล้ว • ผู้โดยสาร ${people} คน • จาก ${pickup} ไป ${dropoff}`;
      summary.innerHTML = `ระบบกำลังจัดเตรียมรถไฟฟ้าสายที่ใกล้ที่สุดและคาดว่าจะถึงในประมาณ ${minutes} นาที`;
    });
  </script>
</body>
</html>
"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"SmartCar demo running at http://127.0.0.1:{PORT}")
        httpd.serve_forever()
