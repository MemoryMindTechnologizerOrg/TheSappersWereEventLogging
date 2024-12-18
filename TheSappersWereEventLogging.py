import subprocess
import time
import logging
import scapy.all as scapy
import csv
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_log_line(line):
    """Parses a line from systemd journal and extracts timestamp and message.

    This function is an example and may need adjustments depending on the
    specific structure of your systemd journal entries.

    Args:
        line (str): A line from the systemd journal output.

    Returns:
        tuple: A tuple containing (timestamp, message).
    """
    # Example parsing logic (adjust based on your systemd journal format)
    parts = line.split(" ", maxsplit=1)
    timestamp = parts[0]
    message = parts[1].strip()
    return timestamp, message


async def log_systemd_events():
    while True:
        try:
            output = subprocess.run(["journalctl", "-n", "10"], capture_output=True, text=True)
            for line in output.stdout.splitlines():
                timestamp, message = parse_log_line(line)
                logger.info(f"Systemd Event: {message}")
                log_to_csv(timestamp, f"Systemd Event: {message}", "systemd_events.csv")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error fetching systemd events: {e}")
        await asyncio.sleep(60)  # Check every minute


async def network_sweep():
    ip_range = "192.168.1.1/24"  # Adjust IP range as needed
    while True:
        try:
            answered_list = scapy.srp(scapy.Ether(dst="FF:FF:FF:FF:FF:FF")/scapy.ARP(pdst=ip_range), timeout=1, verbose=False)[0]
            for client in answered_list:
                ip = client[1].psrc
                mac = client[1].hwsrc
                logger.info(f"Network device: {ip} ({mac})")
                log_to_csv(time.time(), f"Network device: {ip} ({mac})", "network_sweep.csv")
        except Exception as e:
            logger.error(f"Error during network sweep: {e}")
        await asyncio.sleep(60)  # Check every minute

def log_to_csv(timestamp, message, filename):
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, message])

async def main():
    tasks = [
        asyncio.create_task(log_systemd_events()),
        asyncio.create_task(network_sweep())
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())