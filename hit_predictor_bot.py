from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from predictor import predict
import settings


def _is_user_known(context, update):
    username = update.effective_user.username

    with open('permissions.txt') as file:
        users = file.read().rstrip().split('\n')

    if username not in users:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Я тебя не знаю. Напиши @vnkl_iam. '
                                      'Может быть, он нас познакомит.')
        return False
    else:
        return True


def start(update, context):
    if _is_user_known(context, update):
        chat_id = update.effective_message.chat_id
        context.bot.send_message(chat_id=chat_id,
                                 text='Привет!\n\n'
                                      'Я обучен предсказывать хиты с использованием данных российских чартов '
                                      'ВК+ВООМ и Apple Music за 2018-2020 годы. '
                                      'У меня получается делать это с точностью 84%. '
                                      'То есть, если я говорю, что трек 100% хит, то уверен я в этом на 84%. '
                                      'При этом не забывай, что вероятность стать хитом зависит не только от самого '
                                      'трека, но и от масштаба его исполнителя. То есть 34%-ая вероятность трека стать '
                                      'хитом, если его исполняет Егор Крид, это не то же самое, если его исполняет '
                                      'ноунейм. '
                                      'Но при вероятности от 95% трек скорее всего станет хитом, '
                                      'кто бы его не исполнял.\n\n'
                                      'Пришли мне название трека, и я скажу тебе, что я о нем думаю. Имей ввиду, что '
                                      'трек, который ты мне присылаешь, должен быть в Spotify, по-другому я пока не '
                                      'умею, сорян')


def bot_predict(update, context):
    if _is_user_known(context, update):
        chat_id = update.effective_message.chat_id
        text = update.message.text
        if '&' in text:
            context.bot.send_message(chat_id=chat_id,
                                     text='Я не говорил? Символ & использовать нельзя - особенности работы '
                                          'Spotify API. Замени его пробелом или запятой, как там больше подходит '
                                          'на твой взгляд')
        else:
            prediction = predict(text)
            if not prediction:
                context.bot.send_message(chat_id=chat_id,
                                         text='По твоему запросу в Spotify ничего не нашлось((')
            else:
                context.bot.send_message(chat_id=chat_id,
                                         text=f"Вот, что нашлось в Spotify, и что я об этом думаю:\n\n"
                                              f"\n{prediction['artist_name']} - {prediction['track_name']}\n"
                                              f"Вероятность стать хитом:  {prediction['hit_proba'] * 100}%\n\n"
                                              f"--------------\n\n"
                                              f"Обрати внимание, тот ли это трек, который тебе был нужен? "
                                              f"Spotify иногда находит не то, что мы ищем.\n\n"
                                              f"И помни, что я пока не умею учитывать масштаб исполнителя и смысл "
                                              f"текста.")


def main():

    bot = Updater(token=settings.TELEGRAM_TOKEN, request_kwargs=settings.PROXY, use_context=True)
    dp = bot.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, bot_predict))

    bot.start_polling()     # Собсно начинаем обращаться к телеге за апдейтами
    bot.idle()              # Означает, что бот работает до принудительной остановки


if __name__ == '__main__':
    main()
