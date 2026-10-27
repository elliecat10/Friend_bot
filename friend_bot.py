import discord
import random
import asyncio
import requests
import aiohttp

class MyClient(discord.Client):
    #Makes sure that the class works
    def __init__(self, *args, **kwargs):                                        
        super().__init__(*args, **kwargs)

    #Message to wait for user's response
    async def ask_user(self, message, prompt, check, timeout=30):               
        await message.channel.send(prompt)
        try:
            reply = await self.wait_for('message', check=check, timeout=timeout)
            return reply
        except asyncio.TimeoutError:
            await message.channel.send("Response timed out.")
            return None

    #Displays the options menu
    async def prompt_for_choice(self, message, options):                        
        options_message = "\n".join(f"{idx+1}. {option}" for idx, option in enumerate(options))
        await message.channel.send(f"Please choose an option:\n{options_message}")

        def check(m):
            return m.author == message.author and m.channel == message.channel and m.content.isdigit()

        reply = await self.ask_user(message, "Enter the number of your choice:", check)
        if reply and reply.content.isdigit():
            choice_num = int(reply.content)
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1]
        return None

    #Bot working
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Save user and channel context for helper functions
        self.current_message = message

        if message.content.startswith("$hello"):
            await message.channel.send("Hello World!")

        elif message.content.startswith("$options"):
            await self.handle_options()

    async def handle_options(self):
        options = [
            "Dice roll", "Minigame", "Magic 8 Ball", "Joke",
            "Meme", "Word of the day", "Fortune Cookie", "Fun fact",
            "Recommend a film/series/book/song"
        ]
        selected = await self.prompt_for_choice(self.current_message, options)
        if not selected:
            return

        if selected == "Dice roll":
            await self.dice_roll()

        elif selected == "Minigame":
            await self.handle_minigame()

        elif selected == "Magic 8 Ball":
            await self.magic_8_ball()

        elif selected == "Joke":
            await self.tell_joke()

        elif selected == "Meme":
            await self.show_meme()

        elif selected == "Word of the day":
            await self.word_of_the_day()

        elif selected == "Fortune Cookie":
            await self.fortune_cookie()

        elif selected == "Fun fact":
            await self.fun_fact()

        elif selected == "Recommend a film/series/book/song":
            await self.recommendation()

    async def dice_roll(self):
        result = random.randint(1, 6)
        await self.current_message.channel.send(f"🎲 You rolled a {result}!")

    async def handle_minigame(self):
        minigames = ["Guess the number", "Rock, Paper, Scissors", "Slot Machine"]
        choice = await self.prompt_for_choice(self.current_message, minigames)
        if not choice:
            return

        if choice == "Guess the number":
            await self.guess_the_number()
        elif choice == "Rock, Paper, Scissors":
            await self.rps_game()
        elif choice == "Slot Machine":
            await self.slot_machine()

    async def guess_the_number(self):
        secret_number = random.randint(1, 100)
        await self.current_message.channel.send("I'm thinking of a number between 1 and 100. Try to guess it!")

        def check(m):
            return m.author == self.current_message.author and m.channel == self.current_message.channel and m.content.isdigit()

        while True:
            reply = await self.ask_user(self.current_message, "Your guess:", check)
            if not reply:
                break
            try:
                guess = int(reply.content)
                if guess == secret_number:
                    await self.current_message.channel.send(f"🎉 Correct! The number was {secret_number}.")
                    break
                elif guess < secret_number:
                    await self.current_message.channel.send("Higher! Try again.")
                else:
                    await self.current_message.channel.send("Lower! Try again.")
            except:
                await self.current_message.channel.send("Please enter a valid number.")

    async def rps_game(self):
        options = ["✊ (Rock)", "✋ (Paper)", "✌️ (Scissors)"]
        choice_prompt = "\n".join(f"{idx+1}. {option}" for idx, option in enumerate(options))
        await self.current_message.channel.send(f"Choose your move:\n{choice_prompt}")

        def check(m):
            return m.author == self.current_message.author and m.channel == self.current_message.channel and m.content.isdigit()

        reply = await self.ask_user(self.current_message, "Enter your choice number:", check)
        if not reply:
            return

        user_choice_idx = int(reply.content) - 1
        if not (0 <= user_choice_idx < len(options)):
            await self.current_message.channel.send("Invalid choice.")
            return

        user_choice = options[user_choice_idx]
        cpu_choice = random.choice(options)
        await self.current_message.channel.send(f"You chose {user_choice}\nI chose {cpu_choice}")

        # Determine winner
        wins = {
            "✊ (Rock)": "✌️ (Scissors)",
            "✋ (Paper)": "✊ (Rock)",
            "✌️ (Scissors)": "✋ (Paper)"
        }
        if user_choice == cpu_choice:
            await self.current_message.channel.send("It's a tie!")
        elif wins[user_choice] == cpu_choice:
            await self.current_message.channel.send("You win!")
        else:
            await self.current_message.channel.send("I win!")

    async def slot_machine(self):
        symbols = ['🍒', '🍇', '🍉', '7️⃣']
        keep_playing = True
        while keep_playing:
            results = random.choices(symbols, k=3)
            await self.current_message.channel.send(f"🎰 {' | '.join(results)}")
            if results.count('7️⃣') == 3:
                await self.current_message.channel.send("🎉 Jackpot! You won!")
            else:
                await self.current_message.channel.send("Thanks for playing!")

            def check(m):
                return m.author == self.current_message.author and m.channel == self.current_message.channel and m.content.lower() in ['yes', 'no']

            reply = await self.ask_user(self.current_message, "Play again? (yes/no)", check)
            if not reply or reply.content.lower() != 'yes':
                keep_playing = False
                await self.current_message.channel.send("Thanks for playing!")

    async def magic_8_ball(self):
        answers = [
            "Yes, definitely.", "It is decidedly so.", "Without a doubt.",
            "Replay hazy, try again.", "Ask again later.", "Better not tell you now.",
            "My sources say no.", "Outlook not so good.", "Very doubtful."
        ]
        await self.current_message.channel.send("Ask a yes/no question.")
        def check(m):
            return m.author == self.current_message.author and m.channel == self.current_message.channel
        reply = await self.ask_user(self.current_message, "Your question:", check)
        if reply:
            answer = random.choice(answers)
            await self.current_message.channel.send(f"🎱 {answer}")

    async def tell_joke(self):
        url = "https://official-joke-api.appspot.com/jokes/random"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        await self.current_message.channel.send("Couldn't fetch a joke right now.")
                        return
                    data = await response.json()
                
                    # Handle different joke types
                    joke_type = data.get('type')
                    if joke_type == 'single' and 'joke' in data:
                        joke = data['joke']
                    elif joke_type in ['twopart', 'general'] and 'setup' in data and 'punchline' in data:
                        joke = f"{data['setup']} ... {data['punchline']}"
                    else:
                        joke = "Couldn't fetch a joke right now."
                    await self.current_message.channel.send(joke)
        except Exception as e:
            print("Error fetching joke:", e)
            await self.current_message.channel.send("Couldn't fetch a joke right now.")
    
    async def show_meme(self):
        response = requests.get('https://meme-api.com/gimme')
        if response.status_code == 200:
            data = response.json()
            embed = discord.Embed(title=data.get("title", "Meme"))
            embed.set_image(url=data["url"])
            await self.current_message.channel.send(embed=embed)

    async def word_of_the_day(self):
        word_list = [
            ("serendipity", "The occurrence of events by chance in a happy or beneficial way."),
            ("ephemeral", "Lasting for a very short time."),
            ("luminous", "Emitting or reflecting light; shining."),
            ("petrichor", "A pleasant smell that often accompanies the first rain after a dry spell."),
            ("zenith", "The time at which something is most powerful or successful."),
            ("mellifluous", "Sweet or musical; pleasant to hear."),
            ("sonder", "The realization that each passerby has a complex life."),
            ("ineffable", "Too great or extreme to be expressed in words."),
            ("embark", "Begin a journey or adventure."),
            ("cascade", "A small waterfall, typically one of several falling from a height."),
            ("elixir", "A magical or medicinal potion; a remedy believed to cure all ills."),
            ("quintessential", "Representing the most perfect or typical example of a quality."),
            ("silhouette", "The dark shape and outline of someone against a lighter background."),
            ("verdant", "Green with grass or other rich vegetation."),
            ("luminary", "A person who influences others, especially one prominent in a sphere.")
        ]
        word, definition = random.choice(word_list)
        await self.current_message.channel.send(f"Word of the Day: **{word}**\nDefinition: {definition}")

    async def fortune_cookie(self):
        fortunes = [
            "You will find great success in your endeavors.",
            "A surprise awaits you around the corner.",
            "Your hard work will soon pay off.",
            "Now is the time to try something new.",
            "Good news will come to you by mail.",
            "Happiness is headed your way.",
            "Adventure awaits those who seek it.",
            "Your talents will be recognized and rewarded.",
            "A new friendship will blossom soon.",
            "Joy and fulfillment are on your horizon.",
            "Courage will lead you to success.",
            "A fresh start will put you on your way.",
            "Serendipity will bring you something special.",
            "Your positive attitude will lead to success.",
            "Expect the unexpected today."
        ]
        fortune = random.choice(fortunes)
        await self.current_message.channel.send(f"🥠 Your fortune says: {fortune}")

    async def fun_fact(self):
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        if response.status_code == 200:
            data = response.json()
            fact = data["text"]
            await self.current_message.channel.send(f"🤓 Fun Fact: {fact}")

    async def recommendation(self):
        film_list = [
            "The Shawshank Redemption", "Forrest Gump", "The Greatest Showman",
            "Love, Simon", "The Godfather", "Inception", "Happiest season",
            "To All the Boys I've Loved Before", "Disobedience", "Interstellar",
            "Am I Ok?", "The Grand Budapest Hotel", "High School Musical",
            "Camp Rock", "Bottoms", "Toy Story series", "Spirited Away",
            "Inside Out", "Moana", "Coco", "Se7en", "Gone Girl",
            "The Silence of the Lambs", "Fight Club", "Memento", "Parasite",
            "La La Land", "1917", "Get Out", "Knives Out",
            "Spiderman series", "El guardian invisible Trilogy", "El orfanato",
            "As Bestas", "Shin Chan films"
        ]
        series_list = [
            "La Casa de Papel", "Vis a Vis", "El Ministerio del Tiempo", "Vivir sin permiso",
            "HIT", "Las chicas del cable", "SKAM", "El internado", "FRIENDS",
            "Charmed", "Gilmore Girls", "Breaking Bad", "Stranger Things",
            "Heartstopper", "The Last of Us", "Scorpion", "Supergirl", "The Flash",
            "Arrow", "Black Mirror", "Chernobyl", "From", "Dark", "The Boys",
            "Adventure Time", "Inazuma Eleven", "Sex Education", "Young Royals",
            "Outer Banks", "Riverdale", "The Chilling Adventures of Sabrina",
            "The Society", "Euphoria", "Shin Chan", "Spectacular Spiderman"
        ]
        book_list = [
            "To All the Boys I've Loved Before by Jenny Han",
            "The Fault in Our Stars by John Green",
            "Wonder by R.J. Palacio",
            "Divergent by Veronica Roth",
            "Eleanor & Park by Rainbow Rowell",
            "The Book Thief by Markus Zusak",
            "To Kill a Mockingbird by Harper Lee",
            "The Little Prince by Antoine de Saint-Exupéry",
            "Cien años de soledad by Gabriel García Márquez",
            "La sombra del viento by Carlos Ruiz Zafón",
            "El laberinto de los espíritus by Zafón",
            "La chica invisible (Trilogy) by Blue Jeans",
            "Los crimenes de Chopin (Bilogy) by Blue Jeans",
            "El campamento by Blue Jeans",
            "El guardian invisible (Trilogy) by Dolores Redondo",
            "Manual de ghosting para principiantes by Clara Duarte",
            "El acercamiento entre la mujer cactus y el hombre globo by David Martínez Álvarez",
            "Votos en contra by David Martínez Álvarez",
            "El taller de los niños interiores by David Martínez Álvarez",
            "El ciego que describía el mundo by David Martínez Álvarez",
            "ToDa Mi VioLeNciA eS tUyA^^ by Carolina Yuste"
        ]
        song_list = [
            "pa ti toa <3", "MOJA1TA", "Q SOMOS?", "EL BACHATÓN DE LA L",
            "DRAGÓN", "KILLA", "DISCOTEKA", "VERDE",
            "Haz de luz", "Matemática de la carne", "El mejor de tus errores",
            "La calle de la llorería", "Heridas", "Pobre diablo",
            "C'est la vie", "No pido tanto", "No te enamores", "Tanta vida",
            "Niguls", "NUEVAYoL", "DtMF", "BAILE INoLVIDABLE",
            "Un carro bonito", "Haz lo que quieras conmigo", "El día que me olvides",
            "¿Cuántas penas vale tu amor?", "Mi nena", "SABES QUÉ???",
            "CANCIONES SOBRE NADA", "Nana triste", "No Estoy Católica",
            "Que vengan a por mi", "Mirrorball", " Fotos felices",
            "Autarquía emocional", "NI BORRACHO", "AL GOLPITO", "LA GRACIOSA",
            "Sunflower", "What's Up Danger", "Hummingbird", "Am I Dreaming",
            "Self Love"
        ]
        prompt = ("What do you prefer? Type 'film', 'series', 'book', 'song', or 'random'.")
        def check(m):
            return m.author == self.current_message.author and m.channel == self.current_message.channel
        reply = await self.ask_user(self.current_message, prompt, check)
        if not reply:
            return
        reply_content = reply.content.lower()
        if reply_content == "film":
            await self.current_message.channel.send(f"🎬 {random.choice(film_list)}")
        elif reply_content == "series":
            await self.current_message.channel.send(f"📺 {random.choice(series_list)}")
        elif reply_content == "book":
            await self.current_message.channel.send(f"📖 {random.choice(book_list)}")
        elif reply_content == "song":
            await self.current_message.channel.send(f"🎶 {random.choice(song_list)}")
        elif reply_content == "random":
            chosen_category = random.choice(['film', 'series', 'book', 'song'])
            if chosen_category == 'film':
                await self.current_message.channel.send(f"🎬 {random.choice(film_list)}")
            elif chosen_category == 'series':
                await self.current_message.channel.send(f"📺 {random.choice(series_list)}")
            elif chosen_category == 'book':
                await self.current_message.channel.send(f"📖 {random.choice(book_list)}")
            else:
                await self.current_message.channel.send(f"🎶 {random.choice(song_list)}")

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run('TOKEN')