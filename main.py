import json
import os
import discord
from discord.ext import commands
from datetime import datetime

# --- CONFIGURATION ---
# Hardcoded token config inside your private repo
BOT_TOKEN = "MTUxMDQ1NjE2NjcwOTQ2MTA0Mw.GmjkOn.Q72zPZqT8kaCyRs3-wLOacvXZkSYu_mVtKG_xs"

# Render handles files relative to the current workspace directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")

# Automatically generate a backup database structure if the JSON file is missing
if not os.path.exists(HISTORY_FILE):
    print("[NEXUS SYSTEM INFO] chat_history.json not found. Initializing empty log database.")
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"==================================================")
    print(f"[NEXUS SEARCH BOT DISCORD ENGINE ONLINE]")
    print(f"Logged in as username: {bot.user.name}")
    print(f"==================================================")

@bot.command(name="search")
async def search_logs(ctx, *, query: str):
    query = query.lower().strip()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except Exception:
        await ctx.send("❌ Failed to parse log database file.")
        return

    matched_results = [item["raw"] for item in logs if query in item["text"].lower() or query in item["user"].lower()]
    if not matched_results:
        await ctx.send(f"🔍 No historical matches found for query string: `{query}`")
        return

    recent_matches = matched_results[-15:]
    output_payload = "\n".join(recent_matches)

    embed = discord.Embed(
        title=f"🔍 History Match Query: \"{query}\"",
        description=output_payload if len(output_payload) <= 4000 else output_payload[:3950] + "\n*...Truncated*",
        color=3447003
    )
    embed.set_footer(text=f"Displaying {len(recent_matches)} entries | Total Matches Found: {len(matched_results)}")
    await ctx.send(embed=embed)

@bot.command(name="user")
async def user_logs(ctx, username: str, date_filter: str = None):
    target_user = username.lower().strip()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except Exception:
        await ctx.send("❌ Failed to parse log database file.")
        return

    matched_messages = []
    cleaned_date = None
    if date_filter:
        try:
            cleaned_date = datetime.strptime(date_filter.strip(), "%m/%d/%Y").strftime("%m/%d/%Y")
        except ValueError:
            await ctx.send("❌ Invalid date format! Please use **MM/DD/YYYY** format (e.g., `5/31/2026`).")
            return

    for item in logs:
        if item.get("user", "").lower() == target_user:
            if cleaned_date:
                log_date = item.get("date")
                if not log_date or log_date != cleaned_date:
                    continue 
            matched_messages.append(item["raw"])

    if not matched_messages:
        if date_filter:
            await ctx.send(f"🔍 No logs found for user `{username}` on date `{cleaned_date}`.")
        else:
            await ctx.send(f"🔍 No historical database logs found for user `{username}`.")
        return

    recent_logs = matched_messages[-15:]
    output_text = "\n".join(recent_logs)

    title_msg = f"👤 Activity Log for: {username}"
    if date_filter:
        title_msg += f" on {cleaned_date}"

    embed = discord.Embed(
        title=title_msg,
        description=output_text if len(output_text) <= 4000 else output_text[:3950] + "\n*...Truncated*",
        color=15105570
    )
    embed.set_footer(text=f"Showing last {len(recent_logs)} messages out of {len(matched_messages)} total entries.")
    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
