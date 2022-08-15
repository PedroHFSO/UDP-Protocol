import asyncio

async def func1():
    while True:
        print('A')
        await asyncio.sleep(0.1)

async def func2():
    while True:
        print('B')
        await asyncio.sleep(0.1)

async def func3():
    while True:
        print('C')
        await asyncio.sleep(0.1)

async def main():
    task = asyncio.create_task(func1()) #Envio de pacotes
    task_2 = asyncio.create_task(func2()) #Recebimento de ACK
    task_3 = asyncio.create_task(func3()) #Teste de estouro de timeouts
    await asyncio.wait([task, task_2, task_3])
    #await task
    #await task_2
    #await task_3

#print('poha')
asyncio.run(main())