# DANE WEJŚCIOWE:
LEVELS = [int(math.pow(x, 1.5)*20) for x in range(100)] # [0, 20, 56, 103, 160, 223, 293, 370, 452,...]
DATA = {'people': [{'userID': 0, 'xp': 0, 'level': 1}, {'userID': 325291113323692033, 'xp': 23, 'level': 2}, {'userID': 376863468122537985, 'xp': 92, 'level': 3}]} # Przykładowe po inicjalizacji


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    else:
        if not containsBannedWords(message): #tę funkcję olejcie
            for user in DATA['people']:
                if user['userID'] == message.author.id:
                    unique = False
                    user['xp'] += len(message.content.split(" "))
                    level_before = user['level']
                    ## WSTAW TUTAJ PĘTLĘ CZY USER
                    ## POWINIEN JUŻ LVL'UPOWAĆ
                    ## POWINNA ONA ZMIENIAĆ ZAWARTOŚĆ POLA user['level']
                    if level_before != user['level']:
                        await message.channel.send(
                            f"Congratulations {message.author.mention}, you have just hit level {user['level']}!"
                        )
                        write_json(DATA)
                    break
                else:
                    unique = True
            if unique:
                DATA['people'].append({
                    'userID': message.author.id,
                    'xp': len(message.content),
                    'level' : 1
                })
                write_json(DATA)
        else:
            await message.delete()
            await message.channel.send(random.choice(cursingPhrases))
    await bot.process_commands(message)