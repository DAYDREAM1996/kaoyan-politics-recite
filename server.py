import http.server
import socketserver
import os
import sys

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def run_server():
    port = PORT
    for _ in range(10):
        try:
            with socketserver.TCPServer(("", port), Handler) as httpd:
                print("=" * 60)
                print(f"🚀 考研政治24小时极速抢分系统已启动！")
                print("=" * 60)
                print(f"👉 本地浏览器访问地址： http://localhost:{port}")
                print(f"👉 Windows 资源管理器直接打开： explorer.exe index.html")
                print("=" * 60)
                print("键盘快捷键：")
                print("  ← (左键 / A)  : 判断该命题为【错误 / 干扰项】")
                print("  → (右键 / D)  : 判断该命题为【正确 / 真命题】")
                print("  Space / ↓     : 查看下一题")
                print("  S             : 收藏到错题本")
                print("=" * 60)
                print("按 Ctrl + C 即可停止服务。")
                httpd.serve_forever()
        except OSError:
            port += 1

if __name__ == '__main__':
    run_server()
