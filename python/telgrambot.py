from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler , MessageHandler, filters , ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import os
from dotenv import load_dotenv
import mysql.connector
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


# Your new cloud connection!
conn = mysql.connector.connect(
    host="bhavya-bhavya-dc82.l.aivencloud.com",
    user="avnadmin",
    password="AVNS_xjNdufbB05DjYI5AfmQ",
    port=16265, # Aiven's MySQL port
    database="defaultdb"
)
load_dotenv()
TOKEN : Final = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is missing! Check your .env file.")
BOT_USERNAME : Final = '@ssymptom_bot'

#creating commands
#async function used to make our functions asynchronous with the new API

async def start_command(update : Update , context : ContextTypes.DEFAULT_TYPE):
    if update.message:
     await update.message.reply_text("hello thanks for chatting with me how can i help you ? ")



#help command 
async def help_command(update : Update , context : ContextTypes.DEFAULT_TYPE):
    if update.message:
     await update.message.reply_text("you can type or record so that i can respond ")
    
#custom command 
async def custom_command(update : Update , context : ContextTypes.DEFAULT_TYPE):
    if update.message:
     await update.message.reply_text("this is a custom commnd ")


async def log_symptoms_command( update : Update , context : ContextTypes.DEFAULT_TYPE):
  categories = [
      'Pain & Aches', 'Stomach & Digestion', 
      'Cold, Flu & Respiratory', 'General & Neurological', 'Skin'
  ]
  symptoms = [
    # Pain & Aches
    'headache', 'migraine', 'joint pain', 'muscle ache', 'knee pain',
    'shoulder pain', 'neck pain', 'hip pain', 'wrist pain', 'ankle pain',
    'lower back pain', 'upper back pain', 'chest pain', 'earache',
    
    # Stomach & Digestion
    'stomachache', 'nausea', 'vomiting', 'diarrhea', 'constipation',
    'heartburn', 'indigestion', 'bloating', 'loss of appetite',
    
    # Cold, Flu & Respiratory
    'fever', 'cough', 'sore throat', 'runny nose', 'stuffy nose', 
    'shortness of breath', 'wheezing', 'chills', 'sneezing',
    
    # General & Neurological
    'fatigue', 'weakness', 'dizziness', 'trouble sleeping', 'confusion',
    'numbness', 'tingling', 'blurry vision', 'ringing in ears',
    
    # Skin
    'rash', 'itching', 'bruising', 'swelling'
]
  keyboard = []
  for cat in categories:
      # Add "category_" to the callback data so we know it's a category button
      keyboard.append([InlineKeyboardButton(cat, callback_data=f"category_{cat}")])

  reply_markup = InlineKeyboardMarkup(keyboard)
  if update.message:
        await update.message.reply_text('please select what you are feeling right now: ' , reply_markup=reply_markup)
  

#responsess
def handle_response(text:str)-> str:
   processed : str = text.lower()
   if 'hello' in processed:
      return 'hey there!'
   if 'how are you ' in processed:
      return 'i am good'
   if 'sick' in processed:
     return 'can you describe?' 
   symptoms = [
    # Pain & Aches
    'headache', 'migraine', 'joint pain', 'muscle ache', 'knee pain',
    'shoulder pain', 'neck pain', 'hip pain', 'wrist pain', 'ankle pain',
    'lower back pain', 'upper back pain', 'chest pain', 'earache',
    
    # Stomach & Digestion
    'stomachache', 'nausea', 'vomiting', 'diarrhea', 'constipation',
    'heartburn', 'indigestion', 'bloating', 'loss of appetite',
    
    # Cold, Flu & Respiratory
    'fever', 'cough', 'sore throat', 'runny nose', 'stuffy nose', 
    'shortness of breath', 'wheezing', 'chills', 'sneezing',
    
    # General & Neurological
    'fatigue', 'weakness', 'dizziness', 'trouble sleeping', 'confusion',
    'numbness', 'tingling', 'blurry vision', 'ringing in ears',
    
    # Skin
    'rash', 'itching', 'bruising', 'swelling'
]
   for symptom in symptoms:
     if symptom in processed:
       return f'Noted, logging {symptom}.'
   if 'back pain' in processed:
     return 'Noted. is it lower or upper back pain ? '
   
   return 'i dont understand sorry, you can use the custom command.'

DEFAULT_ADVICE = 'Please drink a glass of water and make sure you are resting comfortably. If unsure, consult a doctor.'

async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
      await query.answer()
      data = str(query.data)
      # Ensure Pylance knows this is a string
      symptom_categories = {
        'Pain & Aches': ['headache', 'migraine', 'joint pain', 'muscle ache', 'knee pain', 'shoulder pain', 'neck pain', 'hip pain', 'wrist pain', 'ankle pain', 'lower back pain', 'upper back pain', 'chest pain', 'earache'],
        'Stomach & Digestion': ['stomachache', 'nausea', 'vomiting', 'diarrhea', 'constipation', 'heartburn', 'indigestion', 'bloating', 'loss of appetite'],
        'Cold, Flu & Respiratory': ['fever', 'cough', 'sore throat', 'runny nose', 'stuffy nose', 'shortness of breath', 'wheezing', 'chills', 'sneezing'],
        'General & Neurological': ['fatigue', 'weakness', 'dizziness', 'trouble sleeping', 'confusion', 'numbness', 'tingling', 'blurry vision', 'ringing in ears'],
        'Skin': ['rash', 'itching', 'bruising', 'swelling']
      }

      if data.startswith("category_"):
          category_name = data.replace("category_", "")
          symptoms_in_cat = symptom_categories.get(category_name, [])
          
          keyboard = []
          for i in range (0 , len(symptoms_in_cat) , 2):
            row = []
            symptom1 = symptoms_in_cat[i]
            row.append(InlineKeyboardButton(symptom1.title(), callback_data = symptom1))

            if i + 1 < len(symptoms_in_cat):
              symptom2 = symptoms_in_cat[i+1]
              row.append(InlineKeyboardButton(symptom2.title() , callback_data= symptom2))
              
            keyboard.append(row)
          
          # Add a button to go back to categories
          keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_categories")])
          
          reply_markup = InlineKeyboardMarkup(keyboard)
          await query.edit_message_text(f'Select a symptom under {category_name}:', reply_markup=reply_markup)

      # 2. If user clicked Back
      elif data == "back_to_categories":
          categories = list(symptom_categories.keys())
          keyboard = []
          for cat in categories:
              keyboard.append([InlineKeyboardButton(cat, callback_data=f"category_{cat}")])

          reply_markup = InlineKeyboardMarkup(keyboard)
          await query.edit_message_text('please select a category: ', reply_markup=reply_markup)

      # 3. If user clicked an actual Symptom
      else:
          selected_symptom = data
          symptom_advice = {
            'headache': 'Drink a large glass of water, rest in a quiet, dark room, and apply a cold compress to your forehead.',
            'migraine': 'Drink a large glass of water, rest in a quiet, dark room, and apply a cold compress to your forehead.',
            'stomachache': 'Drink warm water or peppermint tea, and try to sit upright.',
            'bloating': 'Drink warm water or peppermint tea, and try to sit upright.',
            'constipation': 'Drink warm water or peppermint tea, and try to sit upright.',
            'heartburn': 'Sip a small amount of water, stay strictly upright (do not lie down!), and avoid eating anything else for a bit.',
            'muscle ache': 'Stay hydrated, do some very gentle stretching, and apply a warm heating pad to the area.',
            'joint pain': 'Stay hydrated, do some very gentle stretching, and apply a warm heating pad to the area.',
            'knee pain': 'Stay hydrated, do some very gentle stretching, and apply a warm heating pad to the area.',
            'dizziness': 'Please sit or lie down immediately. Sip water slowly and have a small sugary snack if you haven’t eaten.',
            'confusion': 'Please sit or lie down immediately. Sip water slowly and have a small sugary snack if you haven’t eaten.',
            'fever': 'Drink plenty of fluids (water or electrolyte drinks) to stay hydrated and get into bed to rest.',
            'chills': 'Drink plenty of fluids (water or electrolyte drinks) to stay hydrated and get into bed to rest.'
          }


          specific_advice = symptom_advice.get(
             selected_symptom, 
             'Please drink a glass of water and make sure you are resting comfortably.'
      )

      final_message = (
          f"✅ Noted. Logging your {selected_symptom}.\n\n"
          f"💡 **Quick Tip:** {specific_advice}\n\n"
          f"*(Disclaimer: I am just a bot! Please consult a doctor immediately if your symptoms persist or worsen.)*"
      )

      print(f"Logged: {selected_symptom}")
      await query.edit_message_text(text=final_message, parse_mode='Markdown')
# --- DUMMY WEB SERVER FOR RENDER ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is awake and running!")

def keep_alive():
    # Render assigns a port automatically, we catch it here
    port = int(os.environ.get('PORT', 10000)) 
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()
# -----------------------------------
#message 
async def handle_message(update: Update , context : ContextTypes.DEFAULT_TYPE):
   if update.message:
    message_type: str = update.message.chat.type
    if update.message and update.message.text:
     text: str = update.message.text
     print(f'User ({update.message.chat.id}) in {message_type}: "{text}')
     
     if message_type == 'group':
       if BOT_USERNAME in text:
         new_text: str = text.replace(BOT_USERNAME,' ').strip()
         response: str = handle_response(new_text)
       else:
         return
     else:
      response: str = handle_response(text)
    print('Bot:', response)
    await update.message.reply_text(response)


async def error (update: object , context : ContextTypes.DEFAULT_TYPE):
  print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot....')
    
    app = Application.builder().token(TOKEN).build()
    #commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('log_symptoms', log_symptoms_command))
    #messages
    # FIX: Added CallbackQueryHandler so the buttons actually fire your function
    app.add_handler(CallbackQueryHandler(button_click_handler))
    
    #messages
    app.add_handler(MessageHandler(filters.TEXT,handle_message))
    
    #error
    app.add_error_handler(error)
    threading.Thread(target=keep_alive, daemon=True).start()

    #polls the bot
    print('Polling...')
    app.run_polling(poll_interval=5)
