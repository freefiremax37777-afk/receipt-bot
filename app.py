import qrcode
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, send_file, request
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Receipt Bot is running!"

@app.route("/receipt")
def serve_receipt():
    file = request.args.get("file")
    return send_file(f"receipts/{file}", mimetype="image/png")

if not os.path.exists("receipts"):
    os.makedirs("receipts")

BOT_TOKEN = "8350937243:AAFy2_J84BHQncjVjYBWoeDFRkm7c5bbNBM"

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def generate_receipt(name, amount):
    img = Image.open("receipt_template.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, 40)

    draw.text((260, 345), name, fill="black", font=font)
    draw.text((260, 635), f"{amount} ₹", fill="black", font=font)

    file_name = f"receipt_{name}.png"
    img.save(f"receipts/{file_name}")
    return file_name

async def bill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = context.args[0]
        amount = context.args[1]
    except:
        await update.message.reply_text("Use: /bill <name> <amount>")
        return

    file = generate_receipt(name, amount)

    base_url = "https://receipt-bot-cofv.onrender.com"
    link = f"{base_url}/receipt?file={file}"

    qr = qrcode.make(link)
    qr_file = f"qr_{name}.png"
    qr.save(qr_file)

    await update.message.reply_photo(
        photo=open(qr_file, "rb"),
        caption=f"Receipt for {name} | Amount: ₹{amount}"
    )

app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
app_bot.add_handler(CommandHandler("bill", bill))

if __name__ == "__main__":
    import threading
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000))
    flask_thread.start()

    app_bot.run_polling()
