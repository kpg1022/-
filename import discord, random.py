import discord
from discord.ext import commands
import random

# 봇 토큰을 여기에 입력하세요
TOKEN = 'MTM3MzY5MzYxMjE0Mjg4NzE1Nw.GKlRLJ.tc0iuWKBpw-hJT2CZpyw18y6ckltphK0GWdZQw'

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 사용자별 잔액을 저장하는 딕셔너리
user_balances = {}

# 배팅 금액 설정을 위한 딕셔너리
user_bets = {}

@bot.event
async def on_ready():
    print(f'{bot.user}가 로그인되었습니다!')

# 잔액 추가 명령어
@bot.command(name='추가', help='잔액을 추가합니다.')
async def 추가(ctx, amount: int):
    user_id = str(ctx.author.id)

    # 사용자가 잔액을 1달러 이상 추가하려는지 확인
    if amount <= 0:
        await ctx.send("잔액은 1달러 이상 추가해야 합니다.")
        return

    # 잔액 추가
    user_balances[user_id] = user_balances.get(user_id, 0) + amount
    await ctx.send(f"{ctx.author.mention}님, {amount}달러가 잔액에 추가되었습니다. 현재 잔액은 {user_balances[user_id]}달러입니다.")

# !차감 명령어: 잔액에서 차감
@bot.command(name='차감', help='잔액에서 지정된 금액을 차감합니다.')
async def 차감(ctx, amount: int):
    user_id = str(ctx.author.id)

    # 잔액이 존재하는지 확인
    if user_id not in user_balances:
        await ctx.send(f"{ctx.author.mention}님, 잔액이 설정되지 않았습니다. 먼저 !추가 [금액] 명령어로 잔액을 추가해주세요.")
        return

    # 잔액이 충분한지 확인
    if amount <= 0:
        await ctx.send("금액은 1달러 이상이어야 합니다.")
        return

    if user_balances[user_id] < amount:
        await ctx.send(f"{ctx.author.mention}님, 잔액이 부족합니다. 현재 잔액은 {user_balances[user_id]}달러입니다.")
        return

    # 차감
    user_balances[user_id] -= amount
    await ctx.send(f"{ctx.author.mention}님, {amount}달러가 차감되었습니다. 현재 잔액은 {user_balances[user_id]}달러입니다.")

    # 30% 확률로 농담 메시지 추가
    if random.random() < 0.3:
        await ctx.send("하하! 아, 절대 당신을 보고 웃은건 아닙니다. 로봇은 감정이 없거든요.")

@bot.command(name='홀수짝수', help='홀수 짝수 게임을 시작합니다. 배팅 금액을 설정하세요.')
async def 홀수_짝수_게임(ctx):
    user_id = str(ctx.author.id)

    # 사용자가 잔액을 설정하지 않았다면, 잔액을 설정할 수 있도록 안내
    if user_id not in user_balances:
        await ctx.send(f"{ctx.author.mention}님, 게임을 시작하려면 잔액을 먼저 설정해야 합니다.")
        await ctx.send("배팅할 초기 금액을 입력하시겠습니까? !추가 [금액]으로 잔액을 추가할 수 있습니다. 추가하지 않으시려면 !추가안함을 입력하세요.")
        

        try:
            # 사용자 입력 받기 (잔액 추가 여부)
            response_message = await bot.wait_for('message', check=check, timeout=30)
            response = response_message.content.strip().lower()

            if response == '!추가안함':
                await ctx.send(f"{ctx.author.mention}님, 잔액 추가 없이 바로 게임을 시작합니다. 배팅할 금액을 입력해주세요.")
                try:
                    amount = int(response.split()[1])
                    if amount <= 0:
                        await ctx.send("금액은 1달러 이상이어야 합니다.")
                        return
                    user_balances[user_id] = user_balances.get(user_id, 0) + amount
                    await ctx.send(f"{ctx.author.mention}님, {amount}달러가 잔액에 추가되었습니다. 현재 잔액은 {user_balances[user_id]}달러입니다.")
                except (IndexError, ValueError):
                    await ctx.send("금액을 정확히 입력해주세요. 예: !추가 100")
                return  # 이미 !추가 명령어가 처리되었으므로, 추가적인 입력을 받지 않도록 return

            else:
                return
        except TimeoutError:
            await ctx.send("시간 초과! 다시 시도해주세요.")
            return

    # 배팅 명령어 안내
    await ctx.send(f"{ctx.author.mention}님, 이제 배팅할 금액을 !배팅 [금액] 형식으로 입력해주세요.")

@bot.command(name='배팅', help='배팅 금액을 설정합니다.')
async def 배팅(ctx, amount: int):
    user_id = str(ctx.author.id)

    # 사용자가 잔액을 설정하지 않았다면, 게임을 진행할 수 없게 합니다.
    if user_id not in user_balances:
        await ctx.send(f"{ctx.author.mention}님, 먼저 잔액을 설정해야 합니다. !추가 [금액]으로 잔액을 추가해 주세요.")
        return

    # 배팅 금액이 5달러 이상이고, 잔액 내에서 유효한지 확인
    if amount < 5:
        await ctx.send("배팅 금액은 최소 5달러 이상이어야 합니다.")
        return

    if amount > user_balances[user_id]:
        await ctx.send(f"잔액이 부족합니다. 현재 잔액은 {user_balances[user_id]}달러입니다.")
        return

    # 배팅 금액을 설정하고, 게임을 진행
    user_bets[user_id] = amount
    user_balances[user_id] -= amount  # 배팅 금액 차감
    await ctx.send(f"{ctx.author.mention}님, 배팅 금액 {amount}달러가 설정되었습니다. 홀수 또는 짝수를 선택하세요.")

    # 사용자 선택 받기
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        user_choice_message = await bot.wait_for('message', check=check, timeout=30)
        user_choice = user_choice_message.content.strip().lower()

        if user_choice not in ['홀수', '짝수']:
            await ctx.send("잘못된 선택입니다. '홀수' 또는 '짝수'를 선택해야 합니다.")
            return

        # 컴퓨터가 랜덤 숫자 선택
        컴퓨터_숫자 = random.randint(1, 10)
        if 컴퓨터_숫자 % 2 == 0:
            컴퓨터_선택 = '짝수'
        else:
            컴퓨터_선택 = '홀수'

        await ctx.send(f"컴퓨터가 숫자 {컴퓨터_숫자}를 선택했습니다.")

        # 결과 비교
        if user_choice == 컴퓨터_선택:
            user_balances[user_id] += user_bets[user_id] * 2  # 맞히면 배팅 금액의 두 배 추가
            await ctx.send(f"정답입니다! 컴퓨터는 {컴퓨터_선택}를 선택했습니다. {user_bets[user_id] * 2}달러가 추가되었습니다.")
        else:
            await ctx.send(f"아쉽네요. 컴퓨터는 {컴퓨터_선택}를 선택했습니다. 배팅 금액 {user_bets[user_id]}달러가 차감되었습니다.")

        # 배팅 금액 초기화
        del user_bets[user_id]

        # 계속 하시겠습니까? 질문
        await ctx.send(f"{ctx.author.mention}님, 계속 하시겠습니까? !다시 또는 !아니요")

        def check_reply(message):
            return message.author == ctx.author and message.channel == ctx.channel

        response_message = await bot.wait_for('message', check=check_reply, timeout=30)
        response = response_message.content.strip().lower()

        if response == '!다시':
            await 홀수_짝수_게임(ctx)  # 게임을 다시 시작
        elif response == '!아니요':
            # 10% 확률로 농담 메시지 추가
            if random.random() < 0.1:
                await ctx.send("다시 오실텐데....농담입니다! 안녕히 가십시오.")
            else:
                await ctx.send("안녕히 가십시오.")
        else:
            await ctx.send("잘못된 명령어입니다. !다시 또는 !아니요 중 하나를 입력하세요.")

    except TimeoutError:
        await ctx.send("시간 초과! 다시 시도해주세요.")
        # 배팅 금액 초기화
        del user_bets[user_id]

        # 돌림판 배팅 명령어
@bot.command(name="돌림판배팅")
async def spin_bet(ctx, amount: int = None):
    user_id = str(ctx.author.id)

  # 사용자가 잔액을 설정하지 않았다면, 잔액을 설정할 수 있도록 안내
    if user_id not in user_balances:
        await ctx.send(f"{ctx.author.mention}님, 게임을 시작하려면 잔액을 먼저 설정해야 합니다.")
        await ctx.send("배팅할 초기 금액을 입력하시겠습니까? !추가 [금액]으로 잔액을 추가할 수 있습니다. 추가하지 않으시려면 !추가안함을 입력하세요.")
        
        try:
            # 사용자 입력 받기 (잔액 추가 여부)
            response_message = await bot.wait_for('message', check=check, timeout=30)
            response = response_message.content.strip().lower()

            if response == '!추가안함':
                await ctx.send(f"{ctx.author.mention}님, 잔액 추가 없이 바로 게임을 시작합니다. 배팅할 금액을 입력해주세요.")
                try:
                    amount = int(response.split()[1])
                    if amount <= 0:
                        await ctx.send("금액은 1달러 이상이어야 합니다.")
                        return
                    user_balances[user_id] = user_balances.get(user_id, 0) + amount
                    await ctx.send(f"{ctx.author.mention}님, {amount}달러가 잔액에 추가되었습니다. 현재 잔액은 {user_balances[user_id]}달러입니다.")
                except (IndexError, ValueError):
                    await ctx.send("금액을 정확히 입력해주세요. 예: !추가 100")
                return  # 이미 !추가 명령어가 처리되었으므로, 추가적인 입력을 받지 않도록 return

            else:
                return
        except TimeoutError:
            await ctx.send("시간 초과! 다시 시도해주세요.")
            return

    # 배팅 금액이 없다면, 사용자에게 배팅 금액을 입력받음
    if amount is None:
        await ctx.send(f"{ctx.author.mention}님, 배팅할 금액을 입력해주세요. 예: !돌림판배팅 50")
        return
    
    # 배팅 금액이 잔액보다 많으면 오류 메시지
    if amount > user_balances.get(user_id, 0):
        await ctx.send(f"{ctx.author.mention}님, 잔액이 부족합니다. 현재 잔액은 {user_balances.get(user_id, 0)}달러입니다.")
        return

    # "3... 2... 1..." 메시지 출력
    countdown = await ctx.send("3... 2... 1...")
    
    # 돌림판 항목 설정
    options = ['2배', '2배', '2배', '4배', '4배', '10배', '꽝', '꽝', '꽝', '꽝', '꽝']
    
    # 랜덤으로 하나 선택
    result = random.choice(options)

    # 결과 출력
    if result == '꽝':
        user_balances[user_id] -= amount  # 꽝일 경우 배팅 금액 차감
        await countdown.edit(content=f"🎉 돌림판 결과: {result} - 배팅 금액을 잃었습니다. 현재 잔액은 {user_balances[user_id]}달러입니다.")
    else:
        multiplier = int(result.replace('배', ''))  # 예: "10배" -> 10
        winnings = amount * multiplier
        user_balances[user_id] += winnings
        await countdown.edit(content=f"🎉 돌림판 결과: {result} - {winnings}달러를 획득했습니다! 현재 잔액은 {user_balances[user_id]}달러입니다.")

        # !명령어사용법: 모든 명령어의 사용법 출력
@bot.command(name='명령어사용법', help='모든 명령어의 사용법을 알려줍니다.')
async def 명령어사용법(ctx):
    commands_help = """
    **!추가 [금액]**: 사용자 계정에 금액을 추가합니다.
    **!차감 [금액]**: 사용자 계정에서 금액을 차감합니다.
    **!홀수짝수**: 홀수 짝수 게임을 시작합니다. 배팅 금액을 설정해야 합니다.
    **!배팅 [금액]**: 배팅 금액을 설정하고, 홀수 또는 짝수를 선택합니다.
    **!돌림판배팅**: 돌림판 게임을 시작합니다. 배팅 금액을 설정하세요.
    **!명령어사용법**: 봇에서 사용할 수 있는 명령어들의 사용법을 보여줍니다.
    """
    await ctx.send(commands_help)

# 봇 실행
bot.run(TOKEN)
