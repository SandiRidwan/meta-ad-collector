import schedule
import time
from rich.console import Console
from main import run_collection

console = Console()

def job():
    console.print(f"\n[bold yellow]⏰ SCHEDULED RUN STARTED[/bold yellow]")
    run_collection()

# Jadwal run - pilih salah satu:
schedule.every().day.at("08:00").do(job)      # Setiap hari jam 8 pagi
# schedule.every().monday.at("09:00").do(job)  # Setiap Senin
# schedule.every(6).hours.do(job)              # Setiap 6 jam
# schedule.every(30).minutes.do(job)           # Setiap 30 menit

console.print("[bold green]📅 Scheduler aktif. Press Ctrl+C untuk stop.[/bold green]")
console.print(f"Next run: {schedule.next_run()}")

while True:
    schedule.run_pending()
    time.sleep(60)