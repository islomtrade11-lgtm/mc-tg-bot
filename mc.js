import mineflayer from 'mineflayer'
import fs from 'fs'
import fetch from 'node-fetch'

const bot = mineflayer.createBot({
  host: process.env.MC_HOST,
  port: Number(process.env.MC_PORT || 25565),
  username: process.env.MC_USERNAME || "AIBot",
  onlineMode: false
})

bot.on('spawn', () => {
  console.log("🟢 MC bot online")
  setInterval(() => {
    bot.setControlState('jump', true)
    setTimeout(() => bot.setControlState('jump', false), 300)
  }, 60000)
})

bot.on('chat', async (username, message) => {
  if (username === bot.username) return
  if (process.env.AI_ENABLED !== "1") return

  const reply = await groq(message)
  if (reply) bot.chat(reply)
})

setInterval(() => {
  if (fs.existsSync("say.txt")) {
    const msg = fs.readFileSync("say.txt", "utf8")
    bot.chat(msg)
    fs.unlinkSync("say.txt")
  }
}, 1000)

async function groq(text) {
  try {
    const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.GROQ_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "llama-3.1-8b-instant",
        messages: [
          { role: "system", content: "Ты NPC в Minecraft. Коротко." },
          { role: "user", content: text }
        ]
      })
    })
    const data = await res.json()
    return data.choices[0].message.content
  } catch {
    return null
  }
}
