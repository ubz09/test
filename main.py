import discord
from discord.ext import commands
from discord import app_commands
import requests, re, os, time, threading, random, urllib3, configparser, json, concurrent.futures, traceback, warnings, uuid, socket, socks, sys, string, asyncio
from datetime import datetime, timezone
from colorama import Fore, init
from urllib.parse import urlparse, parse_qs
from io import StringIO
from http.cookiejar import MozillaCookieJar
import aiohttp
import io
from flask import Flask
from threading import Thread
import random

# =============================================
# KEEP ALIVE SERVER (Para mantener Replit activo)
# =============================================
app = Flask('')

@app.route('/')
def home():
    return "🤖 MSMC Discord Bot is alive! | Made for Replit"

def run_flask():
    app.run(host='0.0.0.0', port=random.randint(2000, 9000))

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# =============================================
# CONFIGURACIÓN INICIAL
# =============================================
init()

# Variables globales
sFTTag_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"
Combos = []
proxylist = []
banproxies = []
fname = ""
hits,bad,twofa,cpm,cpm1,errors,retries,checked,vm,sfa,mfa,maxretries,xgp,xgpu,other = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
urllib3.disable_warnings()
warnings.filterwarnings("ignore")

# Clase Config
class Config:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

config = Config()

# Clase Capture (simplificada para el ejemplo)
class Capture:
    def __init__(self, email, password, name, capes, uuid, token, type, session):
        self.email = email
        self.password = password
        self.name = name
        self.capes = capes
        self.uuid = uuid
        self.token = token
        self.type = type
        self.session = session
        self.hypixl = None
        self.level = None
        self.cape = None
        self.access = None
        self.banned = None

    def builder(self):
        message = f"Email: {self.email}\nPassword: {self.password}\nName: {self.name}\nCapes: {self.capes}\nAccount Type: {self.type}"
        if self.hypixl: message+=f"\nHypixel: {self.hypixl}"
        if self.level: message+=f"\nHypixel Level: {self.level}"
        if self.cape: message+=f"\nOptifine Cape: {self.cape}"
        if self.access: message+=f"\nEmail Access: {self.access}"
        if self.banned: message+=f"\nHypixel Banned: {self.banned}"
        return message

    async def notify(self, webhook_url):
        try:
            payload = {
                "content": f"🎯 **HIT ENCONTRADO**\nEmail: ||{self.email}||\nPassword: ||{self.password}||\nName: {self.name}\nType: {self.type}",
                "username": "MSMC Discord Bot"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"}) as response:
                    pass
        except Exception as e:
            print(f"Error en notificación: {e}")

# =============================================
# FUNCIONES DE VERIFICACIÓN (Simplificadas)
# =============================================
def getproxy():
    if len(proxylist) == 0:
        return None
    proxy = random.choice(proxylist)
    if isinstance(proxy, dict):
        return proxy
    return {'http': proxy, 'https': proxy}

def authenticate(email, password):
    global hits, bad, checked
    try:
        # Simulación de verificación (en una implementación real usarías las funciones originales)
        time.sleep(0.5)  # Simular delay de verificación
        
        # Ejemplo: 30% de probabilidad de hit
        if random.random() < 0.3:
            hits += 1
            checked += 1
            # Crear objeto capture simulado
            session = requests.Session()
            capture_obj = Capture(
                email=email,
                password=password,
                name="TestPlayer" + str(random.randint(1000, 9999)),
                capes="",
                uuid=str(uuid.uuid4()),
                token="simulated_token",
                type="Normal Minecraft",
                session=session
            )
            return capture_obj, True
        else:
            bad += 1
            checked += 1
            return None, False
    except:
        bad += 1
        checked += 1
        return None, False

# =============================================
# CONFIGURACIÓN DEL BOT
# =============================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def loadconfig():
    global maxretries, config
    maxretries = 5
    config.set('webhook', 'https://discord.com/api/webhooks/your_webhook_here')
    config.set('embed', True)
    config.set('setname', False)
    config.set('setskin', False)
    config.set('hypixelban', False)
    config.set('payment', False)

# =============================================
# COMANDOS DEL BOT
# =============================================
@bot.event
async def on_ready():
    print(f'✅ {bot.user} ha iniciado sesión!')
    print(f'🌐 Replit URL: https://{os.getenv("REPL_SLUG")}.{os.getenv("REPL_OWNER")}.repl.co')
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Error sincronizando comandos: {e}")

@bot.tree.command(name="check", description="Verifica una cuenta de Minecraft")
@app_commands.describe(
    combo="Email:Password de la cuenta a verificar",
    webhook="URL del webhook para enviar resultados (opcional)"
)
async def check(interaction: discord.Interaction, combo: str, webhook: str = None):
    await interaction.response.defer()
    
    try:
        email, password = combo.split(":")
    except ValueError:
        await interaction.followup.send("❌ **Formato incorrecto.** Usa: `email:password`")
        return
    
    # Crear directorio de resultados si no existe
    global fname
    fname = "discord_check"
    if not os.path.exists("results"):
        os.makedirs("results")
    if not os.path.exists(f'results/{fname}'):
        os.makedirs(f'results/{fname}')
    
    # Mostrar que se está verificando
    embed = discord.Embed(
        title="🔍 Verificando Cuenta",
        description=f"Verificando: `{email}`",
        color=discord.Color.blue()
    )
    await interaction.followup.send(embed=embed)
    
    # Realizar la verificación
    capture_obj, hit = authenticate(email.strip(), password.strip())
    
    if hit and capture_obj:
        # Guardar en archivo
        with open(f"results/{fname}/Hits.txt", 'a') as file:
            file.write(f"{email}:{password}\n")
        
        # Enviar webhook si está configurado
        webhook_url = webhook or config.get('webhook')
        if webhook_url and "discord.com/api/webhooks" in webhook_url:
            try:
                await capture_obj.notify(webhook_url)
            except:
                pass
        
        # Enviar embed de éxito
        embed = discord.Embed(
            title="✅ **CUENTA VÁLIDA ENCONTRADA**",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📧 Email", value=f"||{email}||", inline=True)
        embed.add_field(name="🔑 Password", value=f"||{password}||", inline=True)
        embed.add_field(name="🎮 Minecraft Name", value=capture_obj.name or "N/A", inline=True)
        embed.add_field(name="📊 Tipo de Cuenta", value=capture_obj.type or "N/A", inline=True)
        embed.add_field(name="🆔 UUID", value=capture_obj.uuid[:8] + "..." if capture_obj.uuid else "N/A", inline=True)
        embed.set_footer(text="MSMC Discord Bot | Replit Host")
        
        await interaction.edit_original_response(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Cuenta Inválida",
            description=f"**Email:** ||{email}||\nLa cuenta no es válida o no tiene Minecraft.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="MSMC Discord Bot | Replit Host")
        await interaction.edit_original_response(embed=embed)

@bot.tree.command(name="check_file", description="Verifica múltiples cuentas desde un archivo")
@app_commands.describe(
    threads="Número de hilos para verificación (1-10)"
)
async def check_file(interaction: discord.Interaction, threads: int = 5):
    await interaction.response.defer()
    
    # Verificar que haya archivo subido
    if not interaction.message.attachments:
        await interaction.followup.send("❌ **Por favor sube un archivo .txt con las cuentas**")
        return
    
    file = interaction.message.attachments[0]
    
    # Verificar que el archivo sea texto
    if not file.filename.endswith('.txt'):
        await interaction.followup.send("❌ **Por favor sube un archivo .txt**")
        return
    
    # Limitar threads
    threads = max(1, min(threads, 10))
    
    # Descargar y leer el archivo
    try:
        content = await file.read()
        combos = content.decode('utf-8').splitlines()
        combos = [c.strip() for c in combos if ':' in c and c.strip()]
    except Exception as e:
        await interaction.followup.send(f"❌ **Error leyendo el archivo:** {str(e)}")
        return
    
    if not combos:
        await interaction.followup.send("❌ **No se encontraron cuentas válidas en el archivo**")
        return
    
    # Configurar directorio de resultados
    global fname, Combos, hits, bad, checked
    fname = "batch_check"
    Combos = combos
    
    # Reset stats
    hits = 0
    bad = 0
    checked = 0
    
    if not os.path.exists("results"):
        os.makedirs("results")
    if not os.path.exists(f'results/{fname}'):
        os.makedirs(f'results/{fname}')
    
    # Iniciar verificación
    embed = discord.Embed(
        title="🔍 Iniciando Verificación Masiva",
        description=f"**Cuentas a verificar:** {len(combos)}\n**Hilos:** {threads}\n\n⏳ **Procesando...**",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    embed.set_footer(text="Esto puede tomar varios minutos...")
    message = await interaction.followup.send(embed=embed)
    
    # Función para verificar una cuenta
    def check_combo(combo):
        try:
            email, password = combo.split(":", 1)
            return authenticate(email.strip(), password.strip())
        except:
            return None, False
    
    # Verificación en paralelo
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_combo, combo): combo for combo in combos}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            combo = futures[future]
            try:
                future.result()
            except:
                pass
            
            # Actualizar progreso cada 10 combos
            if (i + 1) % 10 == 0:
                progress = f"**Progreso:** {i+1}/{len(combos)}\n**Hits:** {hits}\n**Inválidas:** {bad}"
                
                embed.description = f"**Cuentas a verificar:** {len(combos)}\n**Hilos:** {threads}\n\n{progress}"
                await message.edit(embed=embed)
    
    # Calcular tiempo
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Enviar resultados finales
    result_embed = discord.Embed(
        title="✅ **VERIFICACIÓN COMPLETADA**",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    result_embed.add_field(name="📊 Total Verificado", value=len(combos), inline=True)
    result_embed.add_field(name="✅ Hits", value=hits, inline=True)
    result_embed.add_field(name="❌ Inválidas", value=bad, inline=True)
    result_embed.add_field(name="⏱️ Tiempo", value=f"{elapsed_time:.2f}s", inline=True)
    result_embed.add_field(name="📈 Ratio de Hits", value=f"{(hits/len(combos)*100):.1f}%", inline=True)
    result_embed.add_field(name="🔧 Hilos Usados", value=threads, inline=True)
    
    if hits > 0:
        result_embed.add_field(
            name="💾 Archivos Guardados", 
            value=f"Los hits se guardaron en `results/{fname}/Hits.txt`", 
            inline=False
        )
    
    result_embed.set_footer(text="MSMC Discord Bot | Replit Host")
    
    await message.edit(embed=result_embed)

@bot.tree.command(name="stats", description="Muestra estadísticas del bot")
async def stats(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📊 **ESTADÍSTICAS DEL BOT**",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    embed.add_field(name="✅ Cuentas Verificadas", value=checked, inline=True)
    embed.add_field(name="🎯 Hits", value=hits, inline=True)
    embed.add_field(name="❌ Inválidas", value=bad, inline=True)
    embed.add_field(name="🔧 2FA", value=twofa, inline=True)
    embed.add_field(name="🎮 Xbox Game Pass", value=xgp, inline=True)
    embed.add_field(name="⚡ Xbox Game Pass Ultimate", value=xgpu, inline=True)
    
    if checked > 0:
        success_rate = (hits / checked) * 100
        embed.add_field(name="📈 Tasa de Éxito", value=f"{success_rate:.1f}%", inline=True)
    
    embed.add_field(name="🖥️ Host", value="Replit", inline=True)
    embed.add_field(name="⏰ Uptime", value="24/7 con UptimeRobot", inline=True)
    embed.set_footer(text="MSMC Discord Bot | Replit Host")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Información sobre el bot")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 **MSMC DISCORD BOT**",
        description="Bot de verificación de cuentas Minecraft basado en MSMC",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="🔧 Características", 
        value="""✅ Verificación individual
✅ Verificación masiva por archivo
✅ Webhook notifications
✅ Estadísticas en tiempo real
✅ Hosteado en Replit 24/7""", 
        inline=False
    )
    
    embed.add_field(
        name="📋 Comandos", 
        value="""`/check` - Verificar una cuenta
`/check_file` - Verificar archivo de cuentas  
`/stats` - Ver estadísticas
`/info` - Esta información""", 
        inline=False
    )
    
    embed.add_field(
        name="🌐 Hosting", 
        value="**Replit** + **UptimeRobot**\n✅ 24/7 Uptime\n✅ Gratuito\n✅ Fácil mantenimiento", 
        inline=False
    )
    
    embed.set_footer(text="MSMC Discord Bot | Replit Host")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setup", description="Guía de configuración")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚙️ **GUÍA DE CONFIGURACIÓN**",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="📝 Configuración en Replit", 
        value="""1. **Token del Bot**: Ve a Secrets y añade `DISCORD_TOKEN`
2. **Webhook**: Configura en `config.ini` o usa parámetro
3. **Ejecuta**: Click en \"Run\"
4. **UptimeRobot**: Configura ping cada 5 min""", 
        inline=False
    )
    
    embed.add_field(
        name="🔑 Obtener Token del Bot", 
        value="1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)\n2. Crea una nueva aplicación\n3. Ve a \"Bot\" y copia el token\n4. Añádelo a Replit Secrets", 
        inline=False
    )
    
    embed.add_field(
        name="📁 Formato de Archivos", 
        value="**Para verificación masiva:**\n```email:password\nemail2:password2\n...```", 
        inline=False
    )
    
    embed.set_footer(text="MSMC Discord Bot | Replit Host")
    await interaction.response.send_message(embed=embed)

# =============================================
# INICIALIZACIÓN
# =============================================
@bot.event
async def on_connect():
    try:
        loadconfig()
        print("✅ Configuración cargada correctamente")
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")

# =============================================
# EJECUCIÓN PRINCIPAL
# =============================================
if __name__ == "__main__":
    print("🚀 Iniciando MSMC Discord Bot...")
    print("📁 Directorio de trabajo:", os.getcwd())
    print("🔧 Iniciando servidor keep-alive...")
    
    # Iniciar keep-alive para Replit
    keep_alive()
    
    # Obtener token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        try:
            with open('token.txt', 'r') as f:
                token = f.read().strip()
        except:
            print("❌ ERROR: No se encontró el token del bot")
            print("💡 Solución: Ve a Tools -> Secrets y añade DISCORD_TOKEN")
            print("💡 O crea un archivo token.txt con tu token")
            exit(1)
    
    print("✅ Token encontrado, iniciando bot...")
    bot.run(token)
