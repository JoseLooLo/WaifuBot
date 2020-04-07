import telegram
from telegram import Message
from db import DB
import responses
import util
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, RegexHandler, Filters

def start(update, context):
    try:
        group_id = update.effective_chat.id
        group_name = ""
        if update.effective_chat.title:
            group_name = update.effective_chat.title
        database.newGroup(group_id, group_name)
        waifu_img_ex = "https://cdn.myanimelist.net/images/characters/2/257273.jpg"
        context.bot.send_photo(chat_id=group_id, photo=waifu_img_ex, caption=responses.START)
    except Exception as e:
        print("[ERROR] - {}".format(e))

def help(update, context):
    group_id = update.effective_chat.id
    msg_to_reply = update.message.message_id
    context.bot.send_message(chat_id=group_id, text=responses.HELP, reply_to_message_id=msg_to_reply)

def waifu(update, context):
    try:
        group_id = update.effective_chat.id
        waifu = database.getRandomAnimeWaifu(group_id)
        if waifu is not None:
            waifu_gender = str(waifu[3])
            waifu_img = str(waifu[4])
            if waifu_gender.lower() == 'f':
                context.bot.send_photo(chat_id=group_id, photo=waifu_img, caption=responses.WILD_F_WAIFU)
            elif waifu_gender.lower() == 'm':
                context.bot.send_photo(chat_id=group_id, photo=waifu_img, caption=responses.WILD_M_WAIFU)
            else:
                context.bot.send_photo(chat_id=group_id, photo=waifu_img, caption=responses.WILD_N_WAIFU)

    except Exception as e:
        print("[ERROR] - {}".format(e))

def awaifu(update, context):
    try:
        group_id = update.effective_chat.id
        msg_to_reply = update.message.message_id
        number = -1
        if len(context.args) == 0:
            context.bot.send_message(chat_id=group_id, text=responses.NO_ARGS, reply_to_message_id=msg_to_reply)
            return

        #Verificar se há busca por indice na lista
        for arg in context.args:
            if (arg[0] == '#'):
                try:
                    number = int(arg[1:])
                    context.args.remove(arg)
                    break
                except Exception as e:
                    number = -1
        
        waifus = database.getAnimeWaifusByName(" ".join(context.args))
        if len(waifus) > 5:
            context.bot.send_message(chat_id=group_id, text=responses.MUITAS_WAIFUS, reply_to_message_id=msg_to_reply)
        elif len(waifus) == 1:
            waifu = waifus[0]
            waifu_id = int(waifu[0])
            waifu_name = str(waifu[1])
            waifu_anime = str(waifu[5])
            waifu_gender = str(waifu[3])
            waifu_img = str(waifu[4])
            married = database.haveAnimeWaifuMarried(group_id, waifu_id)

            gender_emoji = responses.EMOJI_N
            if waifu_gender.lower() == 'f':
                gender_emoji = responses.EMOJI_F
            elif waifu_gender.lower() == 'm':
                gender_emoji = responses.EMOJI_M

            if married:
                temp_msg = "{} {} {}\n({})".format(waifu_name, gender_emoji, responses.EMOJI_RING, waifu_anime)
            else:
                temp_msg = "{} {}\n({})".format(waifu_name, gender_emoji, waifu_anime)

            context.bot.send_photo(chat_id=group_id, photo=waifu_img, caption=temp_msg)
        elif len(waifus) == 0:
            context.bot.send_message(chat_id=group_id, text=responses.NO_WAIFU, reply_to_message_id=msg_to_reply)
        else:
            if number != -1 and number <= len(waifus) and number > 0:
                waifu = waifus[number-1]
                waifu_id = int(waifu[0])
                waifu_name = str(waifu[1])
                waifu_anime = str(waifu[5])
                waifu_gender = str(waifu[3])
                waifu_img = str(waifu[4])
                married = database.haveAnimeWaifuMarried(group_id, waifu_id)

                gender_emoji = responses.EMOJI_N
                if waifu_gender.lower() == 'f':
                    gender_emoji = responses.EMOJI_F
                elif waifu_gender.lower() == 'm':
                    gender_emoji = responses.EMOJI_M

                if married:
                    temp_msg = "{} {} {}\n({})".format(waifu_name, gender_emoji, responses.EMOJI_RING, waifu_anime)
                else:
                    temp_msg = "{} {}\n({})".format(waifu_name, gender_emoji, waifu_anime)

                context.bot.send_photo(chat_id=group_id, photo=waifu_img, caption=temp_msg)
            else:
                msg = responses.LIST_WAIFUS_AWAIFU + "\n"
                count = 1
                for waifu in waifus:
                    waifu_id = int(waifu[0])
                    waifu_name = str(waifu[1])
                    waifu_anime = str(waifu[5])
                    married = database.haveAnimeWaifuMarried(group_id, waifu_id)
                    if married:
                        temp_msg = "{}. {} ({}) {}\n".format(str(count), waifu_name, waifu_anime, responses.EMOJI_RING)
                    else:
                        temp_msg = "{}. {} ({})\n".format(str(count), waifu_name, waifu_anime)
                    count+=1
                    msg += temp_msg
                context.bot.send_message(chat_id=group_id, text=msg, reply_to_message_id=msg_to_reply)

    except Exception as e:
        print("[ERROR] - {}".format(e))

def mwaifu(update, context):
    try:
        pass
    except Exception as e:
        print("[ERROR] - {}".format(e))

def marry(update, context):
    try:
        group_id = update.effective_chat.id
        user_id = update.message.from_user.id
        msg_to_reply = update.message.message_id
        waifu = database.getCurrentWaifu(group_id)
        if len(waifu) == 0:
            context.bot.send_message(chat_id=group_id, text=responses.NENHUMA_WAIFU)
        else:
            waifu_id = int(waifu[0])
            waifu_name = str(waifu[1])
            waifu_nickname = str(waifu[2])
            waifu_anime = str(waifu[5])
            if util.compare_names(waifu_name, waifu_nickname, context.args):
                response = database.getMarried(group_id, user_id, waifu_id, waifu_name)
                if response == 0:
                    msg = responses.CASAMENTO + "\nSua nova esposa é "+waifu_name+" ("+waifu_anime+")\nFelicidades ao casal."
                    context.bot.send_message(chat_id=group_id, text=msg, reply_to_message_id=msg_to_reply)
                elif response == 1:
                    context.bot.send_message(chat_id=group_id, text=responses.RUN_MSG_2)
                elif response == 2:
                    context.bot.send_message(chat_id=group_id, text=responses.CASAMENTO_2)
            else:
                if len(context.args) == 0:
                    context.bot.send_message(chat_id=group_id, text=responses.MARRY_WITHOUT_MSG)
                else:
                    context.bot.send_message(chat_id=group_id, text=responses.MARRY_INCORRECT_MSG)

    except Exception as e:
        print("[ERROR] - {}".format(e))

def harem(update, context):
    try:
        usr_name = update.message.from_user.first_name
        if update.message.from_user.username:
            usr_name += ' (@' + update.message.from_user.username + ')'
        
        msg_to_reply = update.message.message_id
        group_name = ""
        if update.effective_chat.title:
            group_name = update.effective_chat.title
        group_id = update.effective_chat.id
        user_id = update.message.from_user.id

        waifus = database.getCurrentHarem(group_id, user_id, 0, 0)

        msg = usr_name + " harem in " + group_name + ":\n"
        count = 1
        for waifu in waifus:
            waifu_name = str(waifu[1])
            waifu_anime = str(waifu[5])
            msg_temp = str(count)+". "+waifu_name+" ("+waifu_anime+")\n"
            msg+=msg_temp
            count += 1
        context.bot.send_message(chat_id=group_id, text=msg, reply_to_message_id=msg_to_reply)

    except Exception as e:
        print("[ERROR] - {}".format(e))

def remove_waifus(context):
    try:
        job = context.job
        groups = database.removeGroupWaifus(job.interval)
        for group_id in groups:
            context.bot.send_message(chat_id=group_id, text=responses.RUN_MSG)

    except Exception as e:
        print("[ERROR] - {}".format(e))

def waifus(context):
    try:
        job = context.job
        groups = database.getReadyGroups(job.interval)

        for group in groups:
            group_id = group
            waifu = database.getRandomAnimeWaifu(group_id)
            if waifu is not None:
                waifu_gender = str(waifu[3])
                waifu_img = str(waifu[4])
                if waifu_gender.lower() == 'f':
                    context.bot.send_photo(chat_id=group_id, photo=waifu_img, caption=responses.WILD_F_WAIFU)
                elif waifu_gender.lower() == 'm':
                    context.bot.send_photo(chat_id=group_id, photo=waifu_img, caption=responses.WILD_M_WAIFU)
                else:
                    context.bot.send_photo(chat_id=group_id, photo=waifu_img, caption=responses.WILD_N_WAIFU)
        
        new_interval = database.newInterval()
        if new_interval == -1:
            new_interval = 60
        job.interval = new_interval
        
    except Exception as e:
        print("[ERROR] - {}".format(e))
    
def main():
    updater = Updater('1134043476:AAFRo6bqfeeiNljslBvLKQEtNuD_jppRHjc', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start',start))          #Initial msg
    dp.add_handler(CommandHandler('help',help))            #Help
    dp.add_handler(CommandHandler('waifu',waifu))          #New waifus
    dp.add_handler(CommandHandler('marry',marry))          #Marry with current waifu
    dp.add_handler(CommandHandler('harem',harem))          #List the current harem
    dp.add_handler(CommandHandler('awaifu',awaifu))          #Show Anime Waifu
    dp.add_handler(CommandHandler('mwaifu',mwaifu))          #Show Manga Waifu
    j = updater.job_queue
    j.run_repeating(remove_waifus, interval=10, first=0)    #Remove waifus
    j.run_repeating(waifus, 1)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    database = DB()
    main()