import telebot
from simpful import *
import logging


TOKEN = 'token'
bot = telebot.TeleBot(TOKEN)

logging.basicConfig(level=logging.DEBUG)

FS = FuzzySystem()

size_small = FuzzySet(function=Trapezoidal_MF(a=-20.6, b=-4.98, c=11.9, d=20.6), term="small")
size_medium = FuzzySet(function=Trapezoidal_MF(a=12.5, b=13.2, c=37.2, d=37.4), term="medium")
size_big = FuzzySet(function=Trapezoidal_MF(a=32.08, b=41.72, c=54.68, d=68.53), term="big")

FS.add_linguistic_variable("size", LinguisticVariable([size_small, size_medium, size_big], universe_of_discourse=[0.1, 50]))

age_puppy = FuzzySet(function=Trapezoidal_MF(a=-6.75, b=-0.75, c=1.085, d=1.2), term="puppy")
age_junior = FuzzySet(function=Trapezoidal_MF(a=0.97, b=1.456, c=3.63, d=4.14), term="junior")
age_adult = FuzzySet(function=Trapezoidal_MF(a=0.362, b=4.32, c=0.478, d=9.731), term="adult")
age_senior = FuzzySet(function=Trapezoidal_MF(a=10.2, b=11.51, c=18.8, d=24.8), term="senior")
FS.add_linguistic_variable("age", LinguisticVariable([age_puppy, age_junior, age_adult, age_senior], universe_of_discourse=[0, 18]))

activity_level_low = FuzzySet(function=Trapezoidal_MF(a=-0.496, b=0.834, c=1.71, d=2.16), term="low")
activity_level_medium = FuzzySet(function=Trapezoidal_MF(a=1.71, b=1.83, c=4.091, d=4.25), term="medium")
activity_level_high = FuzzySet(function=Trapezoidal_MF(a=4.077, b=4.184, c=5.17, d=6.505), term="high")
FS.add_linguistic_variable("activity_level", LinguisticVariable([activity_level_low, activity_level_medium, activity_level_high], universe_of_discourse=[1, 5]))

portion_size_small = FuzzySet(function=Trapezoidal_MF(a=-252, b=-65.6, c=210.4, d=331), term="small")
portion_size_medium = FuzzySet(function=Trapezoidal_MF(a=234, b=257, c=730.5, d=791), term="medium")
portion_size_big = FuzzySet(function=Trapezoidal_MF(a=722, b=768.5, c=1080, d=1300), term="big")
FS.add_linguistic_variable("portion_size", LinguisticVariable([portion_size_small, portion_size_medium, portion_size_big], universe_of_discourse=[0.1, 1000]))

FS.add_rules_from_file(path='fuzzy_logic_rules_list.txt')

@bot.message_handler(commands=['help', 'start'])
def info_msg(message):
    bot.send_message(message.chat.id, "Hello!👋\n"
                                      "I'm a Telegram Bot that can help you calculate a daily food portion for your dog.🐾\n"
                                      "If you want to start click on /run command \n")


@bot.message_handler(commands=['run'])
def run_quiz(message):
    bot.send_message(message.from_user.id, "Let's start!🐾\n"
                                           "If you want to exit, just write me \n/exit\n\n"
                                           "Write a weight of your dog in kg 🐾: \n")
    bot.register_next_step_handler(message, get_size)

def get_size(message):
        if message.text.lower() == '/exit':
            bot.send_message(message.chat.id, "This conversation was stopped")
            return
        global size
        try:
            size = int(message.text)

        except ValueError:
            bot.send_message(message.chat.id, "Check your answer please! You need to choose a number from 1 to 3", parse_mode='Markdown')
            bot.register_next_step_handler(message, get_size)
            return

        bot.send_message(message.chat.id, "Write an age of your dog🐾: \n")
        bot.register_next_step_handler(message, get_age)

def get_age(message):
        if message.text.lower() == '/exit':
            bot.send_message(message.chat.id, "This conversation was stopped")
            return
        global age
        try:
            age = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "Check your answer please! You need to choose a number from 1 to 4", parse_mode='Markdown')
            bot.register_next_step_handler(message, get_age())
            return
        bot.send_message(message.chat.id,
                             "Choose an activity level of your dog🐾: \n"
                         "1-2 - Low activity level\n"
                         "2-4 - Medium activity level\n"
                         "4-5 - High activity level\n", parse_mode='Markdown')
        bot.register_next_step_handler(message, get_activity_level)

def get_activity_level(message):
        if message.text.lower() == '/exit':
            bot.send_message(message.chat.id, "This conversation was stopped")
            return
        global activity_level
        try:
            activity_level = int(message.text)
        except ValueError:
            bot.send_message(message.chat.id, "Check your answer please! You need to choose a number from 1 to 3", parse_mode='Markdown')
            bot.register_next_step_handler(message, get_activity_level)
            return
        create_recommendation(message)

def create_recommendation(message):
    bot.send_message(message.chat.id, "_" + message.chat.first_name + ", let's sum up your data🐾:_\n"
                                      "Breed size " + str(size) + "\n" +
                                      "Age category " + str(age) + "\n" +
                                      "Activity level " + str(activity_level), parse_mode='Markdown')
    variables = ["size", "age", "activity_level"]
    values = [size, age, activity_level]
    for variable, value in zip(variables, values):
        FS.set_variable(variable, value)

    mamdani = FS.Mamdani_inference()
    bot.send_message(message.chat.id, "🐾 Result for you:\n" + get_portion_size(mamdani.get("portion_size")) +
                     "❗ Bot provides only general advice, so for a more accurate calculation, take into account the breed and age of your pet or consult a vet ❗",
                     parse_mode='Markdown')
    bot.send_message(message.chat.id,
                     "If you want to receive a new answer, just enter /run command🐾")

def get_portion_size(c):
        if 0 <= c < 250:
            return "small portion is recommended (to 250gr) 🐾"
        elif 251 <= c < 750:
            return "Medium portion is recommended (to 250 - 730 gr) 🐾"
        elif 750 <= c <= 1000:
            return "Big portion is recommended (to 731 - 1000 gr) 🐾"

@bot.message_handler(commands=['exit'])
@bot.message_handler(func=lambda msg: msg.text is not None and '/' not in msg.text)

def query_handler(message):
        bot.send_message(message.chat.id, "Choose available command please!🐾")
        info_msg(message)

bot.infinity_polling()

